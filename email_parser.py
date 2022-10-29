import csv
import os
import re
from collections import defaultdict
from email import policy
from email.parser import BytesParser
from glob import glob
from typing import Any, Dict, Iterable, List, Literal, Mapping

try:
    import extract_msg
except ImportError:
    extract_msg = None

SupportedEmailExtension = Literal["eml", "msg"]


class EmailParserHandler:
    @staticmethod
    def get_email_files(path: str, extension: SupportedEmailExtension = "eml"):
        return glob(f"{path}/*.{extension.lower()}", recursive=True)

    @staticmethod
    def read_email(file_name: str):
        text = str()
        extension = file_name.split(".").pop()
        with open(file_name, "rb") as fp:
            if extension == "eml":
                msg = BytesParser(policy=policy.default).parse(fp)
                text = msg.as_string()
            elif extension == "msg" and extract_msg:
                text = extract_msg.message.Message(file_name).body or str()

        return text

    @staticmethod
    def fetch_fields(mail: str, field: List[str]) -> Dict[str, str]:
        result: Dict[str, str] = defaultdict(str)
        for key in field:
            try:

                result[key] = ";".join(
                    map(
                        lambda matched: (matched.group(1).strip("\n").strip()),
                        re.finditer(
                            rf'"{key}":((.*?)*\s*(?:"([^"]*)"|(\S+)))',
                            mail,
                            re.I | re.M | re.__builtins__,
                        ),
                    )
                )

            except StopIteration:
                pass

        return dict(result)

    @staticmethod
    def write_to_file(
        field_names: List[str], file_name: str, item_data: Iterable[Mapping[Any, Any]]
    ):
        dict_writer = csv.DictWriter(
            open(file_name, "w", newline=""),
            fieldnames=field_names,
            doublequote=True,
            delimiter=",",
            strict=True,
        )
        dict_writer.writeheader()
        dict_writer.writerows(item_data)


if __name__ == "__main__":
    EMAIL_PATH: str = "."  # directory to search for email
    EXTENSION_TO_LOOK_FOR: SupportedEmailExtension = "eml"
    CONTENT_QUERY: List[str] = [
        "hostname",
        "value",
        "fileWriteEvent/filePath",
        "fileWriteEvent/fullPath",
        "fileWriteEvent/fileName",
        "fileWriteEvent/md5",
        "fileWriteEvent/processPath",
        "fileWriteEvent/userName",
        "fileWriteEvent/parentProcessPath",
    ]  # enter pattern in place of test

    RESULT_FILE: str = "result/result.csv"  # store data in file

    email_files = EmailParserHandler.get_email_files(EMAIL_PATH, EXTENSION_TO_LOOK_FOR)

    CONTENT_QUERY.append("file_name")

    field_items = [
        {
            **EmailParserHandler.fetch_fields(
                EmailParserHandler.read_email(file_name), CONTENT_QUERY
            ),
            "file_name": file_name,
        }
        for file_name in email_files
    ]
    size = len(field_items)

    dir_name = os.path.dirname(RESULT_FILE)
    if dir_name == "":
        dir_name = "."

    file_name = os.path.basename(RESULT_FILE)

    os.makedirs(dir_name, exist_ok=True)

    EmailParserHandler.write_to_file(CONTENT_QUERY, RESULT_FILE, field_items)

    print(
        "SUMMARY:",
        f"FILE READ = {len(email_files)}",
        f"EMAILS READ = {len(field_items)}",
        f"Result file = {RESULT_FILE}",
        sep="\n",
    )
