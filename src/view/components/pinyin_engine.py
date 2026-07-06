from __future__ import annotations

try:
    from Pinyin2Hanzi import DefaultDagParams, all_pinyin, dag

    _PINYIN_ENGINE_AVAILABLE = True
except ImportError:
    _PINYIN_ENGINE_AVAILABLE = False


class PinyinCandidateEngine:
    """封装拼音切分和候选词查询。"""

    def __init__(self, path_num: int = 30):
        self.path_num = path_num
        if _PINYIN_ENGINE_AVAILABLE:
            self.dag_params = DefaultDagParams()
            self.all_pinyins = set(all_pinyin())
        else:
            self.dag_params = None
            self.all_pinyins = set()

    @property
    def available(self) -> bool:
        return _PINYIN_ENGINE_AVAILABLE

    def candidates(self, pinyin_buffer: str) -> list[str]:
        if not pinyin_buffer or not self.available:
            return []

        try:
            pinyin_list = self.split(pinyin_buffer)
            if not pinyin_list:
                return []
            result = dag(self.dag_params, pinyin_list, path_num=self.path_num)
            return ["".join(item.path) for item in result]
        except Exception as exc:
            print(f"Pinyin query error: {exc}")
            return []

    def split(self, text: str) -> list[str]:
        """简单贪婪拼音切分。"""
        result = []
        index = 0
        while index < len(text):
            found = False
            for length in range(max(6, len(text) - index), 0, -1):
                part = text[index : index + length]
                if part in self.all_pinyins:
                    result.append(part)
                    index += length
                    found = True
                    break
            if not found:
                result.append(text[index])
                index += 1
        return result
