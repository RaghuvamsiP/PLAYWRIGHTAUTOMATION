#!/bin/bash
# Generate Allure report in a timestamped folder (no overwriting)
# Usage: bash generate_report.sh         (generate only)
#        bash generate_report.sh --open   (generate + open in browser)

RESULTS_DIR="reports/allure-results"
REPORT_BASE="reports/allure-report"
TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")
REPORT_DIR="$REPORT_BASE/$TIMESTAMP"

# Preserve history from latest previous report
if [ -d "$REPORT_BASE" ]; then
    LATEST=$(ls -td "$REPORT_BASE"/*/ 2>/dev/null | head -1)
    if [ -d "$LATEST/history" ]; then
        echo "[allure] Preserving history from $LATEST"
        mkdir -p "$RESULTS_DIR/history"
        cp -r "$LATEST/history/." "$RESULTS_DIR/history/"
    fi
fi

# Generate new report
echo "[allure] Generating report at $REPORT_DIR"
allure generate "$RESULTS_DIR" -o "$REPORT_DIR"

# List all reports
echo ""
echo "[allure] All reports:"
ls -d "$REPORT_BASE"/*/ 2>/dev/null | while read dir; do echo "  $(basename "$dir")"; done

# Open if requested
if [ "$1" == "--open" ]; then
    echo ""
    echo "[allure] Opening report..."
    allure open "$REPORT_DIR"
else
    echo ""
    echo "To open: allure open $REPORT_DIR"
fi
