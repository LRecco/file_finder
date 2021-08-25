import os
import sys
import time
import re
# Higher recursion limit to loop through whole drive
sys.setrecursionlimit(1500)


class Search:
    keywords: list[str]

    def __init__(self, keywords: list) -> None:
        self.keywords = keywords

    def search_file(self, path: str) -> dict:
        line_count = 0
        rs = {}
        try:
            with open(path, "r", encoding="utf8") as file:
                lines = file.readlines()
                for line in lines:
                    line_count += 1
                    for keyword in self.keywords:
                        if keyword.lower() in line.lower():
                            line = line.strip().replace("\n", "")
                            if path not in rs:
                                rs[path] = [(line, line_count)]
                            else:
                                rs[path].append((line, line_count))
        except UnicodeDecodeError:
            return {}
        except PermissionError:
            return {}
        return rs

    def find(self) -> list[dict]:
        rs: list[dict] = []
        for path, dirs, files in os.walk(os.getcwd()):
            for file in files:
                if "$" in file or "$" in path:
                    continue
                if file.endswith(".txt"):
                    file_path = os.path.join(path, file)
                    # Dictionary of matches
                    matches = self.search_file(file_path)
                    if len(matches) > 0:
                        rs.append(matches)
                        for dir, values in matches.items():
                            print("Directory:", dir)
                            for value in values:
                                print("    Line #: {:<5d} - {}".format(
                                    value[1], value[0]))
                            print()
        return rs


def sum_results(rs: dict) -> int:
    total = 0
    for r_dict in rs:
        for r in r_dict.values():
            total += len(r)
    return total


def parse_arguments() -> list[str]:
    """
    Parse arguments passed to this script. 
    Returns a list of keywords passed in by the user.
    """
    args = [arg for arg in sys.argv[1:]]
    return args


def join_keywords(keywords: list[str]) -> str:
    keywords_string = ""
    for keyword in keywords:
        if " " in keyword:
            keywords_string += '"' + keyword + '"'
        else:
            keywords_string += keyword
        if len(keywords) > 1 and keywords.index(keyword) != len(keywords) - 1:
            keywords_string += ", "
    return keywords_string


def print_results(keywords: list) -> None:
    s = Search(keywords)
    rs = s.find()
    keywords_string = join_keywords(keywords)
    print("Found {} results in {} files with the keywords: {}".format(
        sum_results(rs), len(rs), keywords_string))


def find_search_terms(keywords: str, order_matters: bool = False) -> list:
    """
    Finds open and close quotation marks and joins them as a single 
    search term/keyword.
    """
    if order_matters:
        keywords = keywords.split()
        for keyword in keywords:
            if keyword.startswith(('"', "'")):
                start = keywords.index(keyword)
                for kw in keywords[start:]:
                    if kw.endswith(("'", '"')):
                        end = keywords.index(kw)
                        break
                if end - start <= 1:
                    continue
                keywords[start] = " ".join(keywords[start:end + 1]).replace(
                    '"', "").replace("'", "")
                for i in range(start + 1, end + 1, 1):
                    keywords.pop(start + 1)
            elif len(keyword.strip()) > 0:
                keywords[keywords.index(keyword)] = keyword.replace(
                    '"', "").replace("'", "")
        return keywords
    else:
        matches = re.findall(r'"([a-zA-Z].*)"', keywords)
        matches = matches + re.findall(r"'([a-zA-Z].*)'", keywords)
        for match in matches:
            single_quote = "'" + match + "'"
            double_quote = '"' + match + '"'
            if single_quote in keywords and len(single_quote) > 0:
                keywords = keywords.replace(single_quote, "")
            if double_quote in keywords and len(double_quote) > 0:
                keywords = keywords.replace(double_quote, "")
        results = keywords.split() + matches
        return results


def main():
    """
    Main program execution. If arguments are passed in, 
    parse them and print a result of each keyword passed in.
    """
    start_time = time.time()
    keywords = parse_arguments()
    if len(keywords) > 0:
        print_results(keywords)
    else:
        keywords = input("Enter keywords to search: ")
        start_time = time.time()
        keywords = find_search_terms(keywords, False)
        print_results(keywords)
    print("--- {:.4f} seconds ---".format(time.time() - start_time))


if __name__ == "__main__":
    main()
