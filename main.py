import requests
import asyncio
from lxml import etree

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

    async def download(self, path: str = None) -> str:
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
                raise (e)
        return f"#{self.chapter_name}\n" + "".join([text + "\n" for text in text_lines])


class Book:
    """
    书籍类.

    如果想要下载书籍,请使用download方法.

    Args:
        book_id (int): 该书籍的id
        chapters (list[Chapter]): 书籍的目录,构造时无需传入
    """

    def __init__(self, book_id: int):
        self.book_id: int = book_id
        self.chapters: list[Chapter] = self.get_chapters()

    def __str__(self) -> str:
        return "".join([str(chapter) for chapter in self.chapters])

    def get_chapters(self) -> list[Chapter]:
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
        return [Chapter(name, url) for name, url in zip(chapter_names, chapter_urls)]

    async def download(self, path=None) -> None:
        """
        下载书籍.

        Args:
            path (str): 保存的位置.
        """
        if path == None:
            raise ValueError("未指定path")
        try:
            with open(path, "w", encoding="utf-8") as f:
                for chapter in self.chapters:
                    f.write(await chapter.download())
                    print(f"{chapter.chapter_name} 下载完成.")
        except Exception as e:
            raise (e)
        print(f"已完成书籍{self.book_id}的下载.")


# 下面是测试用例
async def main():
    # 创建书籍对象
    book = Book(714288)
    # 下载书籍
    await book.download("D:\\test.txt")


# 运行
asyncio.run(main())
