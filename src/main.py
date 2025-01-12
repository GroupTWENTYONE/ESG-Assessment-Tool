from textAnalysis.textAnalysis import ESGAnalyzer

def main():

    analyzer = ESGAnalyzer()
    
    analyzer.process_company("Adobe", "ADBE")
    
    # for each company
    #   analyzer process_company


if __name__ == "__main__":
    main()