def expenses_to_csv(df):
    # Exclude extracted document text and local file paths from exports.
    safe = df.copy()
    safe = safe.drop(columns=[c for c in ["extracted_text", "source_path"] if c in safe.columns])
    return safe.to_csv(index=False).encode("utf-8-sig")
