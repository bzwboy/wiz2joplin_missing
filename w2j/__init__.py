##############################
# w2j =  Wiznote to Joplin
#
# https://github.com/zrong/wiz2joplin
##############################

import logging
import sys
from pathlib import Path
import argparse


__autho__ = "zrong, holo"
__version__ = "0.5.1"

work_dir = Path.cwd()
logger = logging.Logger("w2j")
log_file = work_dir.joinpath("w2j.log")
log_handler = logging.FileHandler(log_file, encoding="utf-8")
log_handler.setFormatter(
    logging.Formatter("{asctime} - {funcName} - {levelname} - {message}", style="{")
)
# logger.addHandler(logging.StreamHandler(sys.stderr))
logger.addHandler(log_handler)


parser = argparse.ArgumentParser("w2j", description="Migrate from WizNote to Joplin.")
parser.add_argument(
    "--output",
    "-o",
    type=str,
    metavar="OUTPUT",
    required=True,
    help="The output dir for unziped WizNote file and log file. e.g. ~/wiz2joplin_output or C:\\Users\\zrong\\wiz2joplin_output",
)
parser.add_argument(
    "--wiz-dir",
    "-w",
    type=str,
    metavar="WIZNOTE_DIR",
    required=True,
    help="Set the data dir of WizNote. e.g ~/.wiznote or C:\\Program Files\\WizNote",
)
parser.add_argument(
    "--wiz-user",
    "-u",
    type=str,
    metavar="WIZNOTE_USER_ID",
    required=True,
    help="Set your user id(login email) of WizNote.",
)
parser.add_argument(
    "--joplin-token",
    "-t",
    type=str,
    metavar="JOPLIN_TOKEN",
    required=True,
    help="Set the authorization token to access Joplin Web Clipper Service.",
)
parser.add_argument(
    "--joplin-host",
    "-n",
    type=str,
    metavar="JOPLIN_HOST",
    default="127.0.0.1",
    help="Set the host of your Joplin Web Clipper Service, default is 127.0.0.1",
)
parser.add_argument(
    "--joplin-port",
    "-p",
    type=int,
    metavar="JOPLIN_PORT",
    default=41184,
    help="Set the port of your Joplin Web Clipper Service, default is 41184",
)
parser.add_argument(
    "--location",
    "-l",
    type=str,
    metavar="LOCATION",
    help="Convert the location of WizNote, e.g. /My Notes/. If you use the --all parameter, then skip --location parameter.",
)
parser.add_argument(
    "--location-children",
    "-r",
    action="store_true",
    help="Use with --location parameter, convert all children location of --location.",
)
parser.add_argument(
    "--all", "-a", action="store_true", help="Convert all documents of your WizNote."
)
parser.add_argument(
    "--skip-missing-attachments",
    "-s",
    action="store_true",
    help="Skip documents with missing attachments and images instead of failing.",
)
parser.add_argument(
    "--log-level",
    type=str,
    metavar="LOG_LEVEL",
    default="INFO",
    choices=["CRITICAL", "ERROR", "WARNING", "INFO", "DEBUG"],
    help="Use with --log-level to set the log level, default is warning",
)
args = parser.parse_args()

if sys.platform == "win32":
    from . import wiz_win as wiz
else:
    from . import wiz_mac as wiz
from . import joplin
from . import adapter

__all__ = ["wiz", "joplin", "adapter"]


def setup_logging(log_level: str = "warning"):
    """设置日志记录"""
    log_level = getattr(logging, log_level.upper())
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.FileHandler("w2j.log"), logging.StreamHandler()],
    )

    # 设置第三方库的日志级别
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)

    # 添加性能日志
    perf_logger = logging.getLogger("performance")
    perf_logger.setLevel(logging.INFO)
    perf_handler = logging.FileHandler("performance.log")
    perf_handler.setFormatter(logging.Formatter("%(asctime)s - %(message)s"))
    perf_logger.addHandler(perf_handler)


def main() -> None:
    if args.location is None and args.all == False:
        print(
            "Please set --location to assign the location of WizNote, or use --all to convert all of the documents!"
        )
        return
    wiznote_dir = Path(args.wiz_dir).expanduser()
    if not wiznote_dir.exists():
        print(f"The wiznote directory {wiznote_dir} is not exists!")
        return
    output_dir = Path(args.output).expanduser()
    if not output_dir.exists():
        output_dir.mkdir()
    logger.removeHandler(log_handler)
    newlog_file = output_dir.joinpath("w2j.log")
    print(f"Please read [{newlog_file.resolve()}] to check the conversion states.")
    # Set the corresponding log level
    newlog_handler = logging.FileHandler(newlog_file, encoding="utf-8")
    newlog_handler.setFormatter(
        logging.Formatter("{asctime} - {funcName} - {levelname} - {message}", style="{")
    )
    newlog_handler.setLevel(args.log_level)
    logger.addHandler(newlog_handler)

    # logger.addHandler(logging.FileHandler(newlog_file))

    jda = joplin.JoplinDataAPI(
        host=args.joplin_host, port=args.joplin_port, token=args.joplin_token
    )
    ws = wiz.WizStorage(
        args.wiz_user, wiznote_dir, is_group_storage=False, work_dir=output_dir
    )
    ws.resolve(
        skip_missing_attachments=args.skip_missing_attachments,
        skip_missing_images=args.skip_missing_attachments,
    )
    ad = adapter.Adapter(ws, jda, work_dir=output_dir)
    if args.all:
        ad.sync_all()
    else:
        ad.sync_note_by_location(args.location, args.location_children)

    logger.info("迁移完成！所有笔记已成功同步到 Joplin。")
    print("迁移完成！所有笔记已成功同步到 Joplin。详细信息请查看日志文件。")
