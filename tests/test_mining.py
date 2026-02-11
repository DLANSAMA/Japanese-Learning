import unittest
from src.sentence_mining import mine_sentence

class TestMining(unittest.TestCase):

    def test_verbs(self):
        # v1 (ru-verb)
        self.assertEqual(mine_sentence("食べる", "v1", "eat"), "私は食べます。")
        self.assertEqual(mine_sentence("見る", "v1", "see"), "私は見ます。")

        # v5 (godan)
        self.assertEqual(mine_sentence("飲む", "v5", "drink"), "私は飲みます。")
        self.assertEqual(mine_sentence("書く", "v5", "write"), "私は書きます。")
        self.assertEqual(mine_sentence("泳ぐ", "v5", "swim"), "私は泳ぎます。")
        self.assertEqual(mine_sentence("話す", "v5", "speak"), "私は話します。")
        self.assertEqual(mine_sentence("待つ", "v5", "wait"), "私は待ちます。")
        self.assertEqual(mine_sentence("死ぬ", "v5", "die"), "私は死にます。")
        self.assertEqual(mine_sentence("遊ぶ", "v5", "play"), "私は遊びます。")
        self.assertEqual(mine_sentence("帰る", "v5", "return"), "私は帰ります。")
        self.assertEqual(mine_sentence("会う", "v5", "meet"), "私は会います。")

        # vs (suru)
        self.assertEqual(mine_sentence("勉強する", "vs", "study"), "私は勉強します。")
        self.assertEqual(mine_sentence("勉強", "vs", "study"), "私は勉強します。")

    def test_adjectives(self):
        # i-adj
        self.assertEqual(mine_sentence("高い", "adj-i", "high"), "高いです。")
        self.assertEqual(mine_sentence("美味しい", "adj-i", "tasty"), "美味しいです。")

        # na-adj
        self.assertEqual(mine_sentence("元気", "adj-na", "lively"), "元気です。")
        self.assertEqual(mine_sentence("綺麗", "adj-na", "pretty"), "綺麗です。")

    def test_nouns(self):
        self.assertEqual(mine_sentence("猫", "noun", "cat"), "これは猫です。")
        self.assertEqual(mine_sentence("学校", "noun", "school"), "これは学校です。")

    def test_fallback(self):
        self.assertEqual(mine_sentence("不明", "unknown", "?"), "不明です。")

if __name__ == '__main__':
    unittest.main()
