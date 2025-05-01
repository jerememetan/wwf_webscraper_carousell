import csv

def read_illegal_keywords(file_path):
    """
    Read keywords from the provided CSV file and return them as a list.
    """
    illegal_keywords = []
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                if row:  # Skip empty rows
                    illegal_keywords.append(row[0].strip().lower())  # Add the keyword/phrase, remove any leading/trailing spaces
    except Exception as e:
        print(f"❌ Error reading illegal keywords from {file_path}: {e}")
    return illegal_keywords



def read_weighted_keywords(file_path):
    """
    Reads a CSV with keyword,weight format and returns a dictionary.
    """
    keywords = {}
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                keyword = row['keyword'].strip().lower()
                weight = int(row.get('weight', 1))
                keywords[keyword] = weight
    except Exception as e:
        print(f"❌ Error reading weighted keywords from {file_path}: {e}")
    return keywords


def read_search_terms(file_path):
    """
    Reads a list of search terms from a CSV file (one per line).
    """
    search_terms = []
    try:
        with open(file_path, newline='', encoding='utf-8') as csvfile:
            for row in csvfile:
                term = row.strip()
                if term:
                    search_terms.append(term)
    except Exception as e:
        print(f"❌ Error reading search terms from {file_path}: {e}")
    return search_terms