import sys
from awsglue.utils import getResolvedOptions
from awsglue.context import GlueContext
from awsglue.dynamicframe import DynamicFrame
from awsglue.transforms import SelectFromCollection
from awsgluedq.transforms import EvaluateDataQuality
from pyspark.context import SparkContext
from pyspark.sql import functions as F
from pyspark.sql.window import Window

args = getResolvedOptions(sys.argv, ["JOB_NAME", "bronze_path", "silver_path"])
glueContext = GlueContext(SparkContext.getOrCreate())
spark = glueContext.spark_session

ENABLE_DEDUP = True  # False = test de la gate qualité

# ---------- 1. Lecture bronze ----------
df = spark.read.option("header", "true").csv(args["bronze_path"])
total_in = df.count()

# ---------- 2. Normalisation ----------
normalized = (
    df
    .withColumn("title_normalized",
        F.regexp_replace(F.lower(F.trim(F.col("recording_name"))), r"[^\w\s]", " "))
    .withColumn("title_normalized",
        F.trim(F.regexp_replace(F.col("title_normalized"), r"\s+", " ")))
    .withColumn("artist_primary",
        F.trim(F.regexp_replace(
            F.regexp_replace(F.lower(F.trim(F.col("artist_credit_name"))), r"[^\w\s]", " "),
            r"\s+", " ")))
)

# ---------- 3. Clé métier (pas d'ISWC dans le canonical dump) ----------
with_key = normalized.withColumn(
    "business_key",
    F.concat(F.lit("tn:"), F.col("title_normalized"), F.lit("|ar:"), F.col("artist_primary"))
)

# ---------- 4. Nettoyage ----------
cleaned = with_key.filter(
    (F.col("title_normalized") != "") & F.col("title_normalized").isNotNull()
)
total_cleaned = cleaned.count()

# ---------- 5. Déduplication ----------
if ENABLE_DEDUP:
    window = Window.partitionBy("business_key").orderBy(F.col("score").desc_nulls_last())
    deduped = (
        cleaned
        .withColumn("rn", F.row_number().over(window))
        .filter(F.col("rn") == 1)
        .drop("rn")
    )
else:
    print("[EIP] DEDUP DÉSACTIVÉE (test de la gate)")
    deduped = cleaned

total_out = deduped.count()

print(f"[EIP] entrée={total_in} | écartées={total_in - total_cleaned} | doublons={total_cleaned - total_out} | sortie={total_out}")

# ---------- 6. Gate qualité ----------
ruleset = """
Rules = [
    ColumnExists "business_key",
    ColumnExists "title_normalized",
    IsComplete "title_normalized",
    IsComplete "artist_primary",
    ColumnLength "title_normalized" > 0,
    Uniqueness "business_key" = 1.0,
    RowCount > 0
]
"""

dyf = DynamicFrame.fromDF(deduped, glueContext, "deduped")
dq = EvaluateDataQuality().process_rows(
    frame=dyf,
    ruleset=ruleset,
    publishing_options={
        "dataQualityEvaluationContext": "eip",
        "enableDataQualityCloudWatchMetrics": True,
    },
)

results = SelectFromCollection.apply(dfc=dq, key="ruleOutcomes").toDF()
results.show(truncate=False)

failed = results.filter(F.col("Outcome") != "Passed")
nb_failed = failed.count()

if nb_failed > 0:
    print(f"[EIP] GATE ÉCHOUÉE — {nb_failed} règle(s) en échec, aucune promotion vers silver")
    for row in failed.collect():
        print(f"[EIP]   ✗ {row['Rule']} → {row['FailureReason']}")
    raise Exception(f"DataQualityGateFailed: {nb_failed} règle(s) en échec")

print("[EIP] gate qualité PASSÉE — promotion vers silver")

# ---------- 7. Écriture silver ----------
(deduped
    .select("business_key", "title_normalized", "recording_name", "artist_primary",
            "artist_credit_name", "release_name", "recording_mbid", "release_mbid", "score")
    .write.mode("overwrite").parquet(args["silver_path"]))

print(f"[EIP] {total_out} œuvres écrites dans {args['silver_path']}")