import os
import re
from email import policy
from email.parser import BytesParser
from glob import glob


class EmailParserHandler:
    @staticmethod
    def get_email_files(path: str):
        return glob(f"{path}/*.eml", recursive=True)

    @staticmethod
    def read_email(file_name: str):
        text = str()
        with open(file_name, "rb") as fp:
            msg = BytesParser(policy=policy.default).parse(fp)
            text = msg.as_string()

        return text

    @staticmethod
    def search_query(mail: str, query: str):

        result = re.findall(query, mail, re.I | re.M)
        count = len(result)

        return count


if __name__ == "__main__":
    EMAIL_PATH: str = "."  # directory to search for email
    CONTENT_QUERY: str = ".com"  # enter pattern in place of test
    RESULT_FILE: str = "result/result.txt"  # store data in file
    email_files = EmailParserHandler.get_email_files(EMAIL_PATH)

    get_content_list = list(
        filter(
            lambda mail: EmailParserHandler.search_query(mail, CONTENT_QUERY) != 0,
            [EmailParserHandler.read_email(file_name) for file_name in email_files],
        )
    )
    size = len(get_content_list)
    dir_name = os.path.dirname(RESULT_FILE)
    if dir_name == "":
        dir_name = "."

    file_name = os.path.basename(RESULT_FILE)
    os.makedirs(dir_name, exist_ok=True)
    for index in range(1, size + 1):
        file_name = f"{dir_name}/{index}_{file_name}"
        with open(file_name, "w") as fp:
            fp.write(get_content_list[index - 1])
            fp.close()

    print("INFO: ", f"files written: {size}")
