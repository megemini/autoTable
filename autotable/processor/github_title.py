from __future__ import annotations

from autotable.utils import strtool


class TitleBase:
    def __init__(self, title_content: str) -> None:
        # clean and forma title
        title_content = strtool.clean_title(title_content)

        self.title_content = title_content
        assert self.title_content, RuntimeError("Title content is empty")
        self.multi_table_mode = self.multi_table_mode_judgment()

    def multi_table_mode_judgment(self) -> bool:
        """
        多表模式判断, 主要是 A-1 和 1-3 这两种情况的划分
        """
        continuous_index = self.title_content.find("-")
        if continuous_index == -1:
            return False
        return not (
            self.title_content[continuous_index - 1 : continuous_index].isdigit()
            and self.title_content[continuous_index + 1 : continuous_index + 2].isdigit()
        )

    # 模式分发器
    def distribution_parser(self) -> TitleBase:
        match self.title_content:
            # [No.1, 2-3]
            # [No.1、2-3]
            # [No.1，2-3]  # noqa: RUF003
            # [No.1, 2-3]
            case x if (
                ("、" in x or "," in x or "，" in x) and "-" in x  # noqa: RUF001
            ) and not self.multi_table_mode:
                return MixTitle(x)
            # [No.1]
            case x if x.strip().isdigit():
                return SingleTitle(x)
            # [No.1-2]
            case x if ("-" in x) and not self.multi_table_mode:
                return MultipleTitle(x)
            # [No.1、2]
            case x if "、" in x:
                return MultipleSingleTitle(x, "、")
            # [No.1, 2]
            case x if "," in x:
                return MultipleSingleTitle(x, ",")
            # [No.1，2]  # noqa: RUF003
            case x if "，" in x:  # noqa: RUF001
                return MultipleSingleTitle(x, "，")  # noqa: RUF001
            case x if self.multi_table_mode:
                return SingleTitle(x)
            case _:
                raise RuntimeError(f"Title {self.title_content} is not supported")

    # 转换成数字
    def mate(self) -> list[str]:
        raise NotImplementedError("Please do not call the mate of titleBase")


# 连续标题
class MultipleTitle(TitleBase):
    def __init__(self, title_content: str) -> None:
        super().__init__(title_content)

    def mate(self) -> list[str]:
        title_content = self.title_content.strip()
        assert "-" in title_content
        (start_index, end_index) = title_content.split("-")
        return [str(i) for i in range(int(start_index), int(end_index) + 1)]


# 单标题
class SingleTitle(TitleBase):
    def __init__(self, title_content: str) -> None:
        super().__init__(title_content)

    def mate(self) -> list[str]:
        # [No.1]
        if self.title_content.strip():
            return [self.title_content]
        return []


# 多个单标题
class MultipleSingleTitle(TitleBase):
    def __init__(self, title_content: str, separator: str) -> None:
        super().__init__(title_content)
        self.separator = separator

    def mate(self) -> list[str]:
        res: list[str] = []
        # 切片
        for i in self.title_content.split(self.separator):
            res.append(i.strip())
        return res


# 混合标题
class MixTitle(TitleBase):
    def __init__(self, title_content: str) -> None:
        super().__init__(title_content)

    def mate(self) -> list[str]:
        separator: str = ""
        if "、" in self.title_content:
            separator = "、"
        elif "," in self.title_content:
            separator = ","
        else:
            raise NotImplementedError("Title {self.title_content} is not supported")
        res: list[str] = []
        for i in self.title_content.split(separator):
            res.extend(x for x in TitleBase(i.strip()).distribution_parser().mate())

        return res
