import pytest

from terai_router.normalizer import fold, normalize, skeleton


def test_known_typo_pairs():
    assert normalize('เส็ดหรือยัง') == 'เสร็จหรือยัง'


def test_guard_keeps_correct_word():
    # 'พิม' inside the correct word 'พิมพ์' must not be touched
    assert normalize('พิมพ์ผิด') == 'พิมพ์ผิด'


def test_repeat_collapse():
    assert normalize('ไม่ต้องแล้ววววว').endswith('แล้ว')


def test_return_changes():
    out, ch = normalize('เส็ดยัง', return_changes=True)
    assert out != 'เส็ดยัง' and ch


def test_fold_digits_and_space():
    assert fold('  12  คูณ ๑๒ ') == '0 คูณ 0'
    assert fold('ABC') == 'abc'


def test_skeleton_merges_same_sound():
    assert skeleton('หน่อย') == skeleton('น้อย')
    assert skeleton('ได้') == skeleton('ใด้')


SAFE_PAIR_CASES = [
    # (typo, correct, sentence containing the correct word)
    ("คุน", "คุณ", "ขอบคุณมาก"),
    ("พาษา", "ภาษา", "ฉันเรียนภาษาไทย"),
    ("ฟาย", "ไฟล์", "ส่งไฟล์ให้หน่อย"),
    ("เพ่อม", "เพิ่ม", "เพิ่มข้อมูลใหม่"),
    ("ระว่าง", "ระหว่าง", "ระหว่างทางมีร้านอาหาร"),
    ("บกว่า", "บอกว่า", "เขาบอกว่าไม่มา"),
    ("จิง", "จริง", "เรื่องนี้จริงหรือเปล่า"),
    ("รับสราบ", "รับทราบ", "รับทราบครับ"),
    ("มนุด", "มนุษย์", "มนุษย์ทุกคนเท่าเทียมกัน"),
    ("ขอโทด", "ขอโทษ", "ขอโทษที่มาช้า"),
    ("อังกฤศ", "อังกฤษ", "เขาอยู่ประเทศอังกฤษ"),
    ("ใหน", "ไหน", "ไปไหนมา"),
]


@pytest.mark.parametrize("typo, correct, sentence", SAFE_PAIR_CASES)
def test_safe_pair_is_fixed(typo, correct, sentence):
    assert normalize(typo) == correct


@pytest.mark.parametrize("typo, correct, sentence", SAFE_PAIR_CASES)
def test_safe_pair_correct_word_left_unchanged(typo, correct, sentence):
    assert correct in sentence
    assert normalize(sentence) == sentence