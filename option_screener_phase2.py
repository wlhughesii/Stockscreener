import pandas as pd
import os
from option_utils import get_put_options
from datetime import datetime
from screener_config import (
    CSP_SCORE_THRESHOLD,
    MAX_EXPIRATION_DAYS,
    DELTA_RANGE,
    MIN_ROC,
    MIN_PREMIUM,
    MIN_OI,
    INCLUDE_NEAR_MISS,
    ROC_LOOKBACK_DAYS,
)
from file_utils import get_latest_phase1_file
from excel_utils import save_results_to_excel
from termcolor import cprint

def main():
    phase1_file = get_latest_phase1_file()
    if not phase1_file:
        print("No Phase 1 file found.")
        return

    print(f"Loading: {phase1_file}\n")

    df = pd.read_excel(phase1_file)
    qualified = df[df["Score"] >= CSP_SCORE_THRESHOLD]
    near_miss = df[(df["Score"] >= CSP_SCORE_THRESHOLD - 1) & (df["Score"] < CSP_SCORE_THRESHOLD)] if INCLUDE_NEAR_MISS else pd.DataFrame()

    tickers = qualified["Ticker"].tolist()
    near_tickers = near_miss["Ticker"].tolist()

    print(f"Evaluating {len(tickers)} tickers. Scanning options for {len(tickers)} top scorers", end='')
    if INCLUDE_NEAR_MISS:
        print(f" and {len(near_tickers)} near misses...")
    else:
        print("...")

    results = []
    debug_log = []

    for ticker in tickers + near_tickers:
        is_near = ticker in near_tickers
        try:
            options = get_put_options(ticker, MAX_EXPIRATION_DAYS, DELTA_RANGE, ROC_LOOKBACK_DAYS)
            if not options:
                raise ValueError("No options returned.")

            for option in options:
                failed_criteria = []
                if option['roc'] < MIN_ROC:
                    failed_criteria.append("Low ROC")
                if option['premium'] < MIN_PREMIUM:
                    failed_criteria.append("Low Premium")
                if option['oi'] < MIN_OI:
                    failed_criteria.append("Low OI")

                option['Failed Reason'] = ", ".join(failed_criteria)
                option['Near Miss'] = "Yes" if is_near else "No"

                if not failed_criteria:
                    results.append(option)

                debug_log.append(option)

        except Exception as e:
            cprint(f"[{ticker}] Option API error: 400", "red")
            cprint(f"   {ticker} option data unavailable.", "red")

    if results:
        print("\nSaving qualifying options to Excel...")
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        output_filename = f"results/CSP_Phase2_Options_{timestamp}.xlsx"
        save_results_to_excel(results, output_filename)
        print(f"Results saved to: {output_filename}")
    else:
        print("\nNo qualifying options found.")

    # Save debug log
    debug_log_file = f"results/CSP_Phase2_Debug_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
    pd.DataFrame(debug_log).to_excel(debug_log_file, index=False)
    print(f"Debug log saved to: {debug_log_file}")


if __name__ == "__main__":
    main()

