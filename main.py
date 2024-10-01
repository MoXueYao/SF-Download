import requests
import asyncio
from lxml import etree
from urllib.parse import quote

BASE_URL: str = "https://book.sfacg.com"
BASE_HEADERS: dict = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36"
}


class Chapter:
    """
    章节类.

    如果想要下载章节内容,请使用download方法.
    """

    def __init__(self, chapter_name: str, url: str):
        self.chapter_name = chapter_name
        self.url = BASE_URL + url

    def __str__(self):
        return f"{self.chapter_name} : {self.url}"

    async def download(self, path: str = None, format="txt") -> str:
        """
        下载这个章节,返回章节的内容.

        Args:
            path (str): 下载路径, 默认为None不保存
        """
        response = requests.get(self.url, headers=BASE_HEADERS)
        doc = etree.HTML(response.text)
        text_lines = doc.xpath("//div[@class='article-content font16']/p/text()")
        if path != None:
            try:
                with open(path, "w", encoding="utf-8") as f:
                    f.write(self.chapter_name + "\n")
                    for text in text_lines:
                        f.write(text + "\n")
            except Exception as e:
                raise e
        if format == "txt":
            return f"{self.chapter_name}\n" + "".join(
                ["  " + text + "\n" for text in text_lines]
            )
        if format == "md":
            return f"# {self.chapter_name} <br>\n" + "".join(
                ["&emsp;&emsp;" + text + "<br>\n" for text in text_lines]
            )
        raise Exception("不支持的格式.")


class Book:
    """
    书籍类.

    如果想要下载书籍,请使用download方法.

    Args:
        book (int | str): 该书籍的id或者名称(名称支持模糊搜索,默认为搜索结果的第一项)
        chapters (list[Chapter]): 书籍的目录,构造时无需传入
    """

    def __init__(self, book: int | str):
        if isinstance(book, int):
            self.book_id: int = book
        elif isinstance(book, str):
            self.book_id: int = self.get_book_id(book)
        else:
            raise TypeError("构造书籍时的参数类型错误.")
        self.book_name: str = None
        self.chapters: list[Chapter] = None
        self.get_book_info()

    def __str__(self) -> str:
        return "".join([str(chapter) for chapter in self.chapters])

    def get_book_id(self, name: str):
        """
        获取书籍id.

        该方法无需手动调用,在对象构造时会自动调用.

        如需访问书籍id,请访问对象的book_id属性.
        """
        url = f"https://s.sfacg.com/?Key={quote(name)}&S=1&SS=0"
        response = requests.get(url, headers=BASE_HEADERS)
        doc = etree.HTML(response.text)
        try:
            id = doc.xpath("//strong[@class='F14PX']/a/@href")[0].split("Novel/")[1]
        except IndexError:
            raise Exception("未找到书籍.")
        return int(id)

    def get_book_info(self):
        """
        获取书籍目录.

        该方法无需手动调用,在对象构造时会自动调用.

        如需访问书籍目录,请访问对象的chapters属性.
        """
        url = BASE_URL + f"/Novel/{self.book_id}/MainIndex/"
        response = requests.get(url, headers=BASE_HEADERS)
        doc = etree.HTML(response.text)
        chapter_names = doc.xpath("//div[@class='catalog-list']/ul/li/a/@title")
        chapter_urls = doc.xpath("//div[@class='catalog-list']/ul/li/a/@href")
        self.book_name = doc.xpath(
            "//div[@class='crumbs clearfix']/a[@class='item bold']/text()"
        )[0]
        self.chapters = [
            Chapter(name, url) for name, url in zip(chapter_names, chapter_urls)
        ]

    async def download(self, path=None, format="txt") -> None:
        """
        下载书籍.

        Args:
            path (str): 保存的位置.
            format (str): 下载格式,默认为text,可选md(即markdown)
        """
        i: int = 0
        if path == None and format == "txt":
            path = f"{self.book_name}.txt"
        if path == None and format == "md":
            path = f"{self.book_name}.md"
        try:
            with open(path, "w", encoding="utf-8") as f:
                for chapter in self.chapters:
                    f.write(await chapter.download(format=format))
                    i += 1
                    print(f"已完成: {i/len(self.chapters)*100:.2f}%")
        except Exception as e:
            raise (e)
        print(f"已完成书籍{self.book_name}的下载.")


# 下面是测试用例
async def main():
    # 创建书籍对象
    book = Book("女儿心")
    # 下载书籍,可传入path参数与format参数
    # path为保存位置,默认为当前目录
    # format为下载格式,默认为txt，目前可支持txt与md
    await book.download()


# 运行
asyncio.run(main())
