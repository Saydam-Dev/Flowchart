#!/usr/bin/env python3
import ast
import copy
import json
import math
import os
import random
import re
import sys
import textwrap
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, ttk

APP = "Flowchart Studio"
EXT = ".flow"
CONFIG = os.path.join(os.path.expanduser("~"), ".config", "flowchart-studio", "config.json")
LANG = "tr"


def L(tr, en):
    return tr if LANG == "tr" else en


# ======================================================================
#  Translations: key -> (Türkçe, English)
# ======================================================================
_T = {
    # menus
    "m_file": ("Dosya", "File"), "m_edit": ("Düzenle", "Edit"), "m_view": ("Görünüm", "View"),
    "m_run": ("Çalıştır", "Run"), "m_lang": ("Dil", "Language"), "m_help": ("Yardım", "Help"),
    "f_new": ("Yeni", "New"), "f_open": ("Aç...", "Open..."), "f_save": ("Kaydet", "Save"),
    "f_saveas": ("Farklı kaydet...", "Save as..."), "f_example": ("Örnek aç", "Open example"),
    "f_export": ("Resim olarak dışa aktar (PostScript)...", "Export picture (PostScript)..."),
    "f_quit": ("Çık", "Quit"),
    "e_undo": ("Geri al", "Undo"), "e_redo": ("Yinele", "Redo"),
    "e_delete": ("Seçiliyi sil", "Delete selection"),
    "v_in": ("Yakınlaştır", "Zoom in"), "v_out": ("Uzaklaştır", "Zoom out"),
    "v_reset": ("%100", "100%"), "v_fit": ("Şemayı pencereye sığdır", "Fit chart to window"),
    "r_run": ("Çalıştır", "Run"), "r_step": ("Adım adım", "Step"), "r_stop": ("Durdur", "Stop"),
    "h_how": ("Kullanım kılavuzu", "How to use"),
    # tools and blocks
    "t_select": ("Seç / Taşı", "Select / Move"), "t_connect": ("Bağlan", "Connect"),
    "t_start": ("Başla", "Start"), "t_input": ("Girdi", "Input"), "t_output": ("Yazdır", "Output"),
    "t_process": ("İşlem", "Process"), "t_decision": ("Karar", "Decision"),
    "t_loop": ("Döngü", "Loop"), "t_end": ("Bitir", "End"),
    "s_tools": ("ARAÇLAR", "TOOLS"), "s_blocks": ("BLOKLAR", "BLOCKS"),
    "s_edit": ("DÜZENLE", "EDIT"), "s_zoom": ("YAKINLAŞTIRMA", "ZOOM"),
    # buttons and panels
    "b_run": ("▶ Çalıştır (F5)", "▶ Run (F5)"), "b_step": ("Adım (F6)", "Step (F6)"),
    "b_stop": ("■ Durdur (F8)", "■ Stop (F8)"),
    "b_delay": ("   Blok başına gecikme (ms):", "   Delay per block (ms):"),
    "cb_auto": ("Seçiliden otomatik bağla", "Auto-link from selected"),
    "b_undo": ("↶ Geri al", "↶ Undo"), "b_redo": ("↷ Yinele", "↷ Redo"),
    "b_delete": ("✕ Sil", "✕ Delete"), "b_fit": ("Sığdır", "Fit"), "b_clear": ("Temizle", "Clear"),
    "p_vars": ("Değişkenler", "Variables"), "p_out": ("Çıktı", "Output"),
    "col_name": ("Ad", "Name"), "col_val": ("Değer", "Value"),
    # block texts
    "start_txt": ("Başla", "Start"), "end_txt": ("Bitir", "End"),
    "pre_input": ("Girdi: ", "Input: "), "pre_output": ("Yazdır: ", "Print: "),
    "pre_loop": ("Döngü: ", "Loop: "),
    "lbl_Yes": ("Evet", "Yes"), "lbl_No": ("Hayır", "No"),
    "lbl_Loop": ("Döngü", "Loop"), "lbl_Done": ("Bitti", "Done"),
    # dialogs
    "dt_input": ("Girdi bloğu", "Input block"), "dt_output": ("Yazdır bloğu", "Output block"),
    "dt_process": ("İşlem bloğu", "Process block"), "dt_decision": ("Karar bloğu", "Decision block"),
    "dt_loop": ("Döngü bloğu", "Loop block"),
    "dh_input": ("Klavyeden okunacak değişken(ler).\nÖrnekler:   n      a, b      A[i]",
                 "Variable(s) to read from the keyboard.\nExamples:   n      a, b      A[i]"),
    "dh_output": ('Yazdırılacak şey - yazılar tırnak içinde, değişkenler tırnaksız.\nÖrnek:   "Toplam =", toplam',
                  'What to print - text in quotes, variables without.\nExample:   "Total =", total'),
    "dh_process": ("İfadeler; her satıra bir tane (ya da ; ile ayırın).\nÖrnekler:   toplam = toplam + i      A = dizi(5)      A[0] = 7",
                   "Statements, one per line (or separated by ;).\nExamples:   total = total + i      A = array(5)      A[0] = 7"),
    "dh_decision": ("Evet/Hayır sorusu (koşul).\nÖrnek:   n % 2 == 0",
                    "A yes/no condition.\nExample:   n % 2 == 0"),
    "dh_loop": ("Döngü tanımı:\n  i = 1 to n      i = 10 to 1 step -1      x in A",
                "Loop definition:\n  i = 1 to n      i = 10 to 1 step -1      x in A"),
    "btn_ok": ("Tamam  (Ctrl+Enter)", "OK  (Ctrl+Enter)"), "btn_cancel": ("İptal", "Cancel"),
    "dt_enter": ("Girdi", "Input"),
    "d_enter": ("{name} için bir değer girin:", "Enter a value for {name}:"),
    # validation / syntax messages
    "in_bad": ("Bir ya da daha fazla değişken adı yazın, örn.   n   veya   a, b   veya   A[i]",
               "Enter one or more variable names, e.g.   n   or   a, b   or   A[i]"),
    "p_empty": ("En az bir ifade yazın, örn.   x = 1", "Write at least one statement, e.g.   x = 1"),
    "d_empty": ("Bir koşul yazın, örn.   n > 0", "Write a condition, e.g.   n > 0"),
    "loop_bad": ("Döngü biçimi:   i = 1 to n   veya   i = 1 to n step 2   veya   x in A",
                 "Loop format:   i = 1 to n   or   i = 1 to n step 2   or   x in A"),
    "loop_step0": ("adım 0 olamaz", "step cannot be 0"),
    "se_unsupported": ("'{name}' burada desteklenmiyor (if ve döngüler için oklar, Karar ve Döngü bloklarını kullanın)",
                       "'{name}' is not supported here (use arrows, Decision and Loop blocks for if/loops)"),
    "se_underscore": ("adlar alt çizgi ile başlayamaz", "names may not start with an underscore"),
    "se_call": ("sadece hazır yardımcılar çağrılabilir (abs, sqrt, round, int, len, dizi, randint, ...)",
                "only built-in helpers can be called (abs, sqrt, round, int, len, array, randint, ...)"),
    "se_invalid": ("geçersiz sözdizimi", "invalid syntax"),
    "arr_dims": ("dizi(...) negatif olmayan tamsayı boyutlar ister, örn. dizi(5) veya dizi(3, 4)",
                 "array(...) needs non-negative whole-number sizes, e.g. array(5) or array(3, 4)"),
    # runtime errors
    "ie_one_start": ("Şemada tam olarak bir Başla bloğu olmalı.", "The chart needs exactly one Start block."),
    "ie_no_label": ("Bu bloğun '{label}' oku yok.", "This block has no '{label}' arrow."),
    "ie_no_arrow": ("Bu bloktan çıkan ok yok.", "No arrow leaves this block."),
    "ie_undefined": ("'{name}' değişkeninin henüz değeri yok - önce ona bir değer verin",
                     "'{name}' has no value yet - give it a value first"),
    "ie_zero": ("Sıfıra bölme", "Division by zero"),
    "ie_index": ("Dizi indeksi sınırların dışında (indeksler 0'dan başlar)",
                 "Array index out of range (indexes start at 0)"),
    "ie_overflow": ("Sayı çok büyük", "Number too large"),
    "ie_notiter": ("Bu değer üzerinde döngü kurulamaz", "This value can't be looped over"),
    "ie_prefix": ("Hata: {msg}", "Error: {msg}"),
    "msg_done": ("- bitti -", "- finished -"),
    # status bar
    "st_select": ("Blokları sürükleyin  |  çift tıklayarak düzenleyin  |  bir bloktan diğerine SAĞ TUŞLA sürükleyip bağlayın  |  Delete siler",
                  "Drag blocks to move  |  double-click to edit  |  right-drag from one block to another to connect  |  Delete removes"),
    "st_connect": ("Önce ilk bloğa, sonra gideceği bloğa tıklayın.", "Click the first block, then the block it should lead to."),
    "st_place": ("{name} bloğu koymak için çalışma alanına tıklayın.", "Click on the canvas to place a {name} block."),
    "st_link": ("Şimdi bu bloğun gideceği bloğa tıklayın.", "Now click the block it should lead to."),
    "st_welcome": ("Örnek yüklendi - çalıştırmak için F5'e basın; boş şema için Dosya > Yeni.",
                   "Example loaded - press F5 to run it; File > New for a blank chart."),
    "st_new": ("Yeni şema. Soldan bir blok seçip çalışma alanına tıklayın.",
               "New chart. Pick a block on the left, then click on the canvas."),
    "st_opened": ("Açıldı: {path}", "Opened {path}"), "st_saved": ("Kaydedildi: {path}", "Saved {path}"),
    "st_exported": ("Dışa aktarıldı: {path}   (PDF için:  ps2pdf {name})",
                    "Exported {path}   (convert to PDF with:  ps2pdf {name})"),
    "st_running": ("Çalışıyor...  (Durdur = F8)", "Running...  (Stop = F8)"),
    "st_stopped": ("Durduruldu.", "Stopped."),
    "st_step": ("Turuncu bloğu çalıştırmak için Adım'a basın.", "Press Step to run the orange block."),
    "st_finished": ("{n} blok çalıştırıldı, bitti.", "Finished after {n} blocks."),
    "st_errstop": ("Hata nedeniyle durdu (kırmızı blok).", "The run stopped because of an error (the red block)."),
    "st_cancel": ("Girdi iptal edildi - çalışma durdu.", "Input cancelled - run stopped."),
    # connect errors
    "er_self": ("Bir blok kendine bağlanamaz.", "A block can't point to itself."),
    "er_end": ("Bitir bloğundan ok çıkamaz.", "An End block can't have outgoing arrows."),
    "er_start": ("Başla bloğuna ok gelemez.", "Nothing can point to Start."),
    "er_dup": ("Bu bloklar zaten bağlı.", "Those blocks are already connected."),
    "er_full_decision": ("Karar bloğunun Evet ve Hayır okları zaten var.", "A decision already has its Yes and No arrows."),
    "er_full_loop": ("Döngü bloğunun Döngü ve Bitti okları zaten var.", "A loop already has its Loop and Done arrows."),
    "er_one_start": ("Zaten bir Başla bloğu var.", "There is already a Start block."),
    # files
    "fix_block": ("Önce bu bloğu düzeltin:\n\n{err}", "Fix this block first:\n\n{err}"),
    "bad_file": ("Bu dosya geçerli bir akış şeması değil.", "That file isn't a valid flowchart."),
    "save_err": ("Kaydedilemedi: {err}", "Could not save: {err}"),
    "ask_save": ("Değişiklikler kaydedilsin mi?", "Save changes to the current flowchart first?"),
    "ft_flow": ("Akış şeması", "Flowchart"), "ft_all": ("Tüm dosyalar", "All files"),
    "untitled": ("adsız", "untitled"), "help_title": ("Kullanım kılavuzu", "How to use"),
    # examples
    "ex_sum": ("Toplam 1..N (karar ile döngü)", "Sum 1..N (decision loop)"),
    "ex_fact": ("Faktöriyel (döngü bloğu)", "Factorial (loop block)"),
    "ex_table": ("Çarpım tablosu", "Multiplication table"),
    "ex_evenodd": ("Tek mi çift mi?", "Even or odd"),
    "ex_array": ("Dizi: toplam ve en büyük", "Array: sum and maximum"),
}


def T(key, **kw):
    s = _T[key][0 if LANG == "tr" else 1]
    return s.format(**kw) if kw else s


HELP_TR = """\
ŞEMA OLUŞTURMAK
  1. Soldaki panelden bir blok seçin (Başla, Girdi, Yazdır, İşlem, Karar, Döngü, Bitir),
     sonra çalışma alanına tıklayın. Yazıyı girin, Ctrl+Enter ile onaylayın.
  2. "Seçiliden otomatik bağla" açıkken yeni blok seçili bloğa kendiliğinden bağlanır.
     Elle bağlamak için: bir bloktan diğerine SAĞ TUŞLA sürükleyin ya da soldaki
     "Bağlan" aracıyla önce ilk bloğa, sonra ikinciye tıklayın.
  3. Karar bloğunun ilk oku "Evet", ikincisi "Hayır" olur.
     Döngü bloğunun ilk oku "Döngü" (gövde), ikincisi "Bitti" (çıkış) olur.
     Okun üstüne çift tıklayınca etiketler yer değiştirir.
  4. Bloğu düzenlemek için çift tıklayın, taşımak için sürükleyin. Boş alanı sürükleyerek
     kaydırırsınız. Delete seçili bloğu ya da oku siler.

YAKINLAŞTIRMA
  Ctrl + fare tekerleği, Ctrl + / Ctrl -, ya da soldaki + / - / Sığdır düğmeleri.
  Ctrl+0 = %100.

ÇALIŞTIRMA
  Çalıştır (F5) şemayı çalıştırır. Adım (F6) bir seferde tek blok çalıştırır; turuncu blok
  sıradaki bloktur. Durdur (F8) çalışmayı bitirir. Gecikme çubuğu hızı ayarlar
  (0 = en hızlı). Değişkenler sağda canlı görünür.

BLOK YAZILARI  (Python tarzı ifadeler)
  Girdi    n         a, b         A[i]          (sayılar otomatik tanınır)
  İşlem    toplam = toplam + i       satır başına bir ifade ya da  a = 1; b = 2
  Karar    n % 2 == 0      i <= 10      x > 0 and y > 0
  Yazdır   "Toplam:", toplam          f"Alan = {en * boy}"
  Döngü    i = 1 to n       i = 10 to 1 step -1       x in A
           (to = "...e kadar", step = adım;  "x in A" dizinin her elemanı için döner)

DİZİLER
  A = dizi(5)          5 elemanlı, sıfırla dolu dizi (indeksler 0..4)
  M = dizi(3, 4)       3x4 matris
  A = [4, 9, 2]        elle tanımlama
  A[0] = 7      A[i] = A[i] + 1      M[1][2] = 5      len(A)      ekle(A, 5)
  A[i], A[j] = A[j], A[i]            iki elemanın yerini değiştirir
  Girdi bloğuna  A[i]  yazarak dizinin elemanına değer okuyabilirsiniz
  (Döngü bloğuyla birlikte: Döngü  i = 0 to 4   Girdi  A[i]).

İŞLEVLER
  abs min max round int float str len sum sorted range sqrt floor ceil sin cos tan
  log log10 exp factorial gcd pi randint(a, b) rand()   dizi(...) / array(...)
  Türkçe takma adlar: uzunluk  karekok  mutlak  rastgele  sirala  ekle

KISAYOLLAR
  Ctrl+N/O/S yeni/aç/kaydet     Ctrl+Z/Y geri al/yinele     Esc  Seç aracına dön
"""

HELP_EN = """\
BUILDING A CHART
  1. Pick a block in the left panel (Start, Input, Output, Process, Decision, Loop, End),
     then click on the canvas. Type its text and press Ctrl+Enter.
  2. With "Auto-link from selected" ticked, a new block connects from the selected one.
     To connect by hand: right-drag from one block onto another, or use the Connect tool
     on the left (click the first block, then the second).
  3. A Decision's first arrow is "Yes", the second "No".
     A Loop's first arrow is "Loop" (the body), the second is "Done" (the exit).
     Double-click an arrow to swap the two labels.
  4. Double-click a block to edit it, drag it to move it. Drag the empty background to pan.
     Delete removes the selected block or arrow.

ZOOM
  Ctrl + mouse wheel, Ctrl + / Ctrl -, or the + / - / Fit buttons on the left. Ctrl+0 = 100%.

RUNNING
  Run (F5) executes the chart. Step (F6) runs one block at a time; the orange block is the
  one that runs next. Stop (F8) ends the run. The delay slider sets the speed (0 = fastest).
  Variables are shown live on the right.

WRITING BLOCK TEXT  (Python-style expressions)
  Input     n         a, b         A[i]        (numbers are detected automatically)
  Process   total = total + i      one statement per line, or   a = 1; b = 2
  Decision  n % 2 == 0      i <= 10      x > 0 and y > 0
  Output    "Total:", total          f"Area = {w * h}"
  Loop      i = 1 to n       i = 10 to 1 step -1       x in A
            ("x in A" repeats once for every element of the array)

ARRAYS
  A = array(5)         array of 5 zeros (indexes 0..4)
  M = array(3, 4)      3x4 matrix
  A = [4, 9, 2]        define by hand
  A[0] = 7      A[i] = A[i] + 1      M[1][2] = 5      len(A)      append(A, 5)
  A[i], A[j] = A[j], A[i]            swap two elements
  Put  A[i]  in an Input block to read a value into an array element
  (together with a Loop block:  Loop  i = 0 to 4   Input  A[i]).

FUNCTIONS
  abs min max round int float str len sum sorted range sqrt floor ceil sin cos tan
  log log10 exp factorial gcd pi randint(a, b) rand()   array(...) / dizi(...)
  Turkish aliases: uzunluk  karekok  mutlak  rastgele  sirala  ekle

SHORTCUTS
  Ctrl+N/O/S new/open/save     Ctrl+Z/Y undo/redo     Esc  back to the Select tool
"""


# ======================================================================
#  Settings
# ======================================================================
def load_config():
    global LANG
    try:
        with open(CONFIG, encoding="utf-8") as fh:
            LANG = json.load(fh).get("lang", LANG)
    except (OSError, ValueError, AttributeError):
        pass
    if LANG not in ("tr", "en"):
        LANG = "tr"


def save_config():
    try:
        os.makedirs(os.path.dirname(CONFIG), exist_ok=True)
        with open(CONFIG, "w", encoding="utf-8") as fh:
            json.dump({"lang": LANG}, fh)
    except OSError:
        pass


# ======================================================================
#  Safe expression engine (flowchart text is parsed, never trusted blindly)
# ======================================================================
def _safe_pow(a, b):
    if isinstance(a, int) and isinstance(b, int) and b > 0 and abs(a) > 1:
        if b * math.log2(abs(a)) > 200000:
            raise OverflowError("number too large")
    return a ** b


def _factorial(n):
    if n > 20000:
        raise OverflowError("factorial too large")
    return math.factorial(n)


def _append(lst, value):
    lst.append(value)


def _array(*dims):
    if not dims or any(not isinstance(d, int) or isinstance(d, bool) or d < 0 for d in dims):
        raise ValueError(T("arr_dims"))
    total = 1
    for d in dims:
        total *= d
    if total > 2000000:
        raise OverflowError("array too large")

    def make(i):
        if i == len(dims) - 1:
            return [0] * dims[i]
        return [make(i + 1) for _ in range(dims[i])]

    return make(0)


def _count(start, end, step):
    if step == 0:
        raise ValueError(T("loop_step0"))
    v = start
    if step > 0:
        while v <= end:
            yield v
            v += step
    else:
        while v >= end:
            yield v
            v += step


SAFE = {
    "abs": abs, "min": min, "max": max, "round": round, "int": int, "float": float,
    "str": str, "bool": bool, "len": len, "sum": sum, "sorted": sorted, "list": list,
    "range": range, "pow": _safe_pow, "sqrt": math.sqrt, "floor": math.floor,
    "ceil": math.ceil, "sin": math.sin, "cos": math.cos, "tan": math.tan,
    "log": math.log, "log10": math.log10, "exp": math.exp, "factorial": _factorial,
    "gcd": math.gcd, "pi": math.pi, "e": math.e, "randint": random.randint,
    "rand": random.random, "append": _append, "array": _array, "dizi": _array,
    "uzunluk": len, "karekok": math.sqrt, "mutlak": abs, "rastgele": random.randint,
    "sirala": sorted, "ekle": _append, "_pw": _safe_pow,
}

_OK = (ast.Module, ast.Expression, ast.Expr, ast.Assign, ast.AugAssign, ast.BinOp,
       ast.UnaryOp, ast.BoolOp, ast.Compare, ast.IfExp, ast.Call, ast.Name, ast.Constant,
       ast.Tuple, ast.List, ast.Dict, ast.Subscript, ast.Slice, ast.JoinedStr,
       ast.FormattedValue, ast.keyword, ast.Load, ast.Store, ast.operator, ast.unaryop,
       ast.boolop, ast.cmpop)


class _PowGuard(ast.NodeTransformer):
    """Route ** through _safe_pow so a typo like 9**9**9 cannot freeze the app."""

    def visit_BinOp(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Pow):
            call = ast.Call(ast.Name("_pw", ast.Load()), [node.left, node.right], [])
            return ast.copy_location(call, node)
        return node

    def visit_AugAssign(self, node):
        self.generic_visit(node)
        if isinstance(node.op, ast.Pow) and isinstance(node.target, ast.Name):
            load = ast.Name(node.target.id, ast.Load())
            call = ast.Call(ast.Name("_pw", ast.Load()), [load, node.value], [])
            return ast.copy_location(ast.Assign([node.target], call), node)
        return node


def _validate(tree):
    for node in ast.walk(tree):
        if not isinstance(node, _OK):
            raise SyntaxError(T("se_unsupported", name=type(node).__name__))
        if isinstance(node, ast.Name) and node.id.startswith("_"):
            raise SyntaxError(T("se_underscore"))
        if isinstance(node, ast.Call) and not (isinstance(node.func, ast.Name)
                                               and node.func.id in SAFE):
            raise SyntaxError(T("se_call"))


def compile_code(src, mode):
    src = textwrap.dedent(src).strip()
    tree = ast.parse(src, mode=mode)
    _validate(tree)
    tree = ast.fix_missing_locations(_PowGuard().visit(tree))
    return compile(tree, "<flowchart>", mode)


def split_top(s):
    """Split on commas that are not inside brackets or quotes."""
    parts, cur, depth, quote = [], [], 0, None
    for ch in s:
        if quote:
            cur.append(ch)
            if ch == quote:
                quote = None
        elif ch in "\"'":
            quote = ch
            cur.append(ch)
        elif ch in "([{":
            depth += 1
            cur.append(ch)
        elif ch in ")]}":
            depth -= 1
            cur.append(ch)
        elif ch == "," and depth == 0:
            parts.append("".join(cur).strip())
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur).strip())
    return [p for p in parts if p]


def parse_target(src):
    """An Input target: a variable (n) or an array element (A[i], M[i][j])."""
    tree = ast.parse(src.strip(), mode="eval")
    _validate(tree)
    node = tree.body
    if not isinstance(node, (ast.Name, ast.Subscript)):
        raise SyntaxError(T("in_bad"))
    return node


def compile_assign(node):
    node = copy.deepcopy(node)
    node.ctx = ast.Store()
    mod = ast.Module(body=[ast.Assign(targets=[node], value=ast.Name("_in", ast.Load()))],
                     type_ignores=[])
    mod = ast.fix_missing_locations(_PowGuard().visit(mod))
    return compile(mod, "<flowchart>", "exec")


def compile_slice(node):
    expr = ast.Expression(body=copy.deepcopy(node.slice))
    expr = ast.fix_missing_locations(_PowGuard().visit(expr))
    return compile(expr, "<flowchart>", "eval")


_COUNT = re.compile(r"^([^\W\d]\w*)\s*=\s*(.+?)\s+to\s+(.+?)(?:\s+(?:step|ad[ıi]m)\s+(.+))?$",
                    re.I | re.S)
_EACH = re.compile(r"^([^\W\d]\w*)\s+in\s+(.+)$", re.S)


def parse_loop(text):
    """('count', var, start, end, step)  or  ('each', var, sequence)."""
    t = " ".join(text.split())
    m = _COUNT.match(t)
    spec = None
    if m:
        spec = ("count", m.group(1), m.group(2), m.group(3), m.group(4) or "1")
    else:
        m = _EACH.match(t)
        if m:
            spec = ("each", m.group(1), m.group(2))
    if spec is None or spec[1].startswith("_"):
        raise SyntaxError(T("loop_bad"))
    return spec


def friendly(e):
    msg = e.msg or ""
    return T("se_invalid") if msg == "invalid syntax" else (msg or T("se_invalid"))


def check_text(kind, text):
    """Return an error message for a block's text, or None if it is fine."""
    t = text.strip()
    try:
        if kind == "input":
            parts = split_top(t)
            if not parts:
                return T("in_bad")
            for p in parts:
                parse_target(p)
        elif kind == "output":
            if t:
                compile_code("(" + t + ",)", "eval")
        elif kind == "process":
            if not t:
                return T("p_empty")
            compile_code(t, "exec")
        elif kind == "decision":
            if not t:
                return T("d_empty")
            compile_code(t, "eval")
        elif kind == "loop":
            for src in parse_loop(t)[2:]:
                compile_code(src, "eval")
    except SyntaxError as e:
        return friendly(e)
    except Exception as e:  # noqa: BLE001
        return str(e)
    return None


def parse_value(s):
    s = s.strip()
    for conv in (int, float):
        try:
            return conv(s)
        except ValueError:
            pass
    return s


def fmt(v):
    try:
        s = repr(v) if isinstance(v, str) else str(v)
    except ValueError:
        s = "<too large>"
    return s if len(s) <= 140 else s[:137] + "..."


# ======================================================================
#  The interpreter: walks the arrows one block at a time
# ======================================================================
PAIR = {"decision": ("Yes", "No"), "loop": ("Loop", "Done")}


class FlowError(Exception):
    def __init__(self, nid, msg):
        super().__init__(msg)
        self.nid = nid


class Interpreter:
    def __init__(self, nodes, edges, ask, emit):
        self.nodes = {n["id"]: dict(n) for n in nodes}
        self.out = {}
        for e in edges:
            self.out.setdefault(e["src"], []).append(dict(e))
        starts = [n["id"] for n in nodes if n["type"] == "start"]
        if len(starts) != 1:
            raise FlowError(None, T("ie_one_start"))
        self.cur = starts[0]
        self.prev = None
        self.vars = {}
        self.glob = {"__builtins__": {}}
        self.glob.update(SAFE)
        self.ask, self.emit = ask, emit
        self.cache = {}
        self.loops = {}
        self.bodies = {}
        self.steps = 0

    # ---- helpers
    def code(self, n, mode, src):
        key = (n["id"], mode, src)
        if key not in self.cache:
            self.cache[key] = compile_code(src, mode)
        return self.cache[key]

    def ev(self, n, src):
        return eval(self.code(n, "eval", src), self.glob, self.vars)

    def target(self, n, src):
        key = (n["id"], "target", src)
        if key not in self.cache:
            node = parse_target(src)
            if isinstance(node, ast.Subscript):
                self.cache[key] = (compile_assign(node), compile_slice(node), ast.unparse(node.value))
            else:
                self.cache[key] = (compile_assign(node), None, node.id)
        return self.cache[key]

    def body(self, nid):
        """Blocks reachable from the loop's body arrow without passing the loop itself."""
        if nid not in self.bodies:
            seen = set()
            stack = [e["dst"] for e in self.out.get(nid, []) if e["label"] == "Loop"]
            while stack:
                x = stack.pop()
                if x == nid or x in seen:
                    continue
                seen.add(x)
                stack.extend(e["dst"] for e in self.out.get(x, []))
            self.bodies[nid] = seen
        return self.bodies[nid]

    def make_iter(self, n):
        spec = parse_loop(n["text"])
        if spec[0] == "each":
            return iter(self.ev(n, spec[2]))
        return _count(self.ev(n, spec[2]), self.ev(n, spec[3]), self.ev(n, spec[4]))

    # ---- one step
    def step(self):
        """Run the current block. Returns 'ok', 'done' or 'cancel'."""
        n = self.nodes[self.cur]
        t, nid = n["type"], n["id"]
        self.steps += 1
        label = None
        try:
            if t == "end":
                return "done"
            if t == "input":
                for src in split_top(n["text"]):
                    assign, sl, base = self.target(n, src)
                    name = base
                    if sl is not None:
                        idx = eval(sl, self.glob, self.vars)
                        if isinstance(idx, tuple):
                            idx = ", ".join(str(v) for v in idx)
                        name = f"{base}[{idx}]"
                    s = self.ask(name)
                    if s is None:
                        return "cancel"
                    self.glob["_in"] = parse_value(s)
                    exec(assign, self.glob, self.vars)
            elif t == "output":
                txt = n["text"].strip()
                vals = ()
                if txt:
                    vals = eval(self.code(n, "eval", "(" + txt + ",)"), self.glob, self.vars)
                self.emit(" ".join(str(v) for v in vals))
            elif t == "process":
                exec(self.code(n, "exec", n["text"]), self.glob, self.vars)
            elif t == "decision":
                label = "Yes" if self.ev(n, n["text"]) else "No"
            elif t == "loop":
                it = self.loops.get(nid)
                if it is None or self.prev not in self.body(nid):
                    it = self.loops[nid] = self.make_iter(n)
                try:
                    self.vars[parse_loop(n["text"])[1]] = next(it)
                    label = "Loop"
                except StopIteration:
                    self.loops.pop(nid, None)
                    label = "Done"
        except FlowError:
            raise
        except NameError as e:
            raise FlowError(nid, T("ie_undefined", name=getattr(e, "name", None) or str(e)))
        except ZeroDivisionError:
            raise FlowError(nid, T("ie_zero"))
        except IndexError:
            raise FlowError(nid, T("ie_index"))
        except OverflowError:
            raise FlowError(nid, T("ie_overflow"))
        except Exception as e:  # noqa: BLE001
            if t == "loop" and isinstance(e, TypeError):
                raise FlowError(nid, T("ie_notiter"))
            raise FlowError(nid, f"{type(e).__name__}: {e}")

        outs = self.out.get(nid, [])
        if t in PAIR:
            nxt = next((e for e in outs if e["label"] == label), None)
            if nxt is None:
                raise FlowError(nid, T("ie_no_label", label=T("lbl_" + label)))
        else:
            if not outs:
                raise FlowError(nid, T("ie_no_arrow"))
            nxt = outs[0]
        self.prev = nid
        self.cur = nxt["dst"]
        return "ok"


# ======================================================================
#  Looks
# ======================================================================
COLORS = {"start": "#c8e6c9", "end": "#ffcdd2", "input": "#bbdefb", "output": "#ffe0b2",
          "process": "#fff9c4", "decision": "#e1bee7", "loop": "#b2dfdb"}
OUTLINE = {"start": "#2e7d32", "end": "#c62828", "input": "#1565c0", "output": "#e65100",
           "process": "#f9a825", "decision": "#6a1b9a", "loop": "#00695c"}
BASE = {"start": (120, 46), "end": (120, 46), "input": (160, 54), "output": (160, 54),
        "process": (160, 54), "decision": (180, 90), "loop": (170, 56)}
SIDE_BLOCKS = ["start", "input", "output", "process", "decision", "loop", "end"]
PLACE = set(SIDE_BLOCKS)
LABEL_COLOR = {"Yes": "#2e7d32", "No": "#c62828", "Loop": "#00695c", "Done": "#e65100"}
SIDE_BG = "#eceff1"
GRID = 10


def shade(color, f):
    r, g, b = (int(color[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % (int(r * f), int(g * f), int(b * f))


def example(eid):
    """(nodes, edges) for a built-in example, texts in the current language."""
    tot = L("toplam", "total")
    if eid == "sum":
        nodes = [("start", "", 260, 50), ("input", "n", 260, 130),
                 ("process", f"{tot} = 0\ni = 1", 260, 215), ("decision", "i <= n", 260, 330),
                 ("process", f"{tot} = {tot} + i\ni = i + 1", 260, 450),
                 ("output", L(f'"Toplam:", {tot}', f'"Sum is", {tot}'), 520, 330), ("end", "", 520, 430)]
        edges = [(0, 1, ""), (1, 2, ""), (2, 3, ""), (3, 4, "Yes"), (3, 5, "No"), (4, 3, ""), (5, 6, "")]
    elif eid == "fact":
        nodes = [("start", "", 260, 50), ("input", "n", 260, 130), ("process", "f = 1", 260, 215),
                 ("loop", "i = 1 to n", 260, 310), ("process", "f = f * i", 260, 420),
                 ("output", L('"Faktöriyel:", f', '"Factorial:", f'), 520, 310), ("end", "", 520, 400)]
        edges = [(0, 1, ""), (1, 2, ""), (2, 3, ""), (3, 4, "Loop"), (3, 5, "Done"), (4, 3, ""), (5, 6, "")]
    elif eid == "table":
        nodes = [("start", "", 260, 50), ("input", "n", 260, 130), ("loop", "i = 1 to 10", 260, 230),
                 ("output", 'n, "x", i, "=", n * i', 260, 340), ("end", "", 520, 230)]
        edges = [(0, 1, ""), (1, 2, ""), (2, 3, "Loop"), (2, 4, "Done"), (3, 2, "")]
    elif eid == "evenodd":
        nodes = [("start", "", 300, 50), ("input", "n", 300, 130), ("decision", "n % 2 == 0", 300, 240),
                 ("output", L('"Çift"', '"Even"'), 150, 360), ("output", L('"Tek"', '"Odd"'), 450, 360),
                 ("end", "", 300, 470)]
        edges = [(0, 1, ""), (1, 2, ""), (2, 3, "Yes"), (2, 4, "No"), (3, 5, ""), (4, 5, "")]
    else:  # array
        big = L("buyuk", "biggest")
        nodes = [("start", "", 260, 50),
                 ("process", f"A = [4, 9, 2, 7, 5]\n{big} = A[0]\n{tot} = 0", 260, 140),
                 ("loop", "x in A", 260, 260), ("process", f"{tot} = {tot} + x", 260, 360),
                 ("decision", f"x > {big}", 260, 470), ("process", f"{big} = x", 260, 590),
                 ("output", L(f'"Toplam =", {tot}, "  En büyük =", {big}',
                              f'"Total =", {tot}, "  Biggest =", {big}'), 540, 260),
                 ("end", "", 540, 350)]
        edges = [(0, 1, ""), (1, 2, ""), (2, 3, "Loop"), (2, 6, "Done"), (3, 4, ""), (4, 5, "Yes"),
                 (4, 2, "No"), (5, 2, ""), (6, 7, "")]
    return ([{"id": i + 1, "type": t, "text": s or {"start": "Start", "end": "End"}.get(t, ""),
              "x": x, "y": y} for i, (t, s, x, y) in enumerate(nodes)],
            [{"src": a + 1, "dst": b + 1, "label": lb} for a, b, lb in edges])


EXAMPLE_IDS = ["fact", "table", "sum", "evenodd", "array"]


def seg_dist(px, py, x0, y0, x1, y1):
    dx, dy = x1 - x0, y1 - y0
    if dx == 0 and dy == 0:
        return math.hypot(px - x0, py - y0)
    t = max(0, min(1, ((px - x0) * dx + (py - y0) * dy) / (dx * dx + dy * dy)))
    return math.hypot(px - (x0 + t * dx), py - (y0 + t * dy))


def validate_chart(d):
    ids = set()
    for n in d["nodes"]:
        if n["type"] not in COLORS or not isinstance(n["text"], str):
            raise ValueError("bad block")
        n["id"], n["x"], n["y"] = int(n["id"]), float(n["x"]), float(n["y"])
        ids.add(n["id"])
    for e in d["edges"]:
        if e["src"] not in ids or e["dst"] not in ids:
            raise ValueError("bad arrow")
        e.setdefault("label", "")


def center_window(win, parent):
    """Put a dialog in the middle of the main window (kept fully on screen)."""
    win.update_idletasks()
    w, h = win.winfo_reqwidth(), win.winfo_reqheight()
    x = parent.winfo_rootx() + (parent.winfo_width() - w) // 2
    y = parent.winfo_rooty() + (parent.winfo_height() - h) // 2
    x = max(0, min(x, win.winfo_screenwidth() - w))
    y = max(0, min(y, win.winfo_screenheight() - h))
    win.geometry(f"+{x}+{y}")


# ======================================================================
#  Dialogs
# ======================================================================
class TextDialog(tk.Toplevel):
    def __init__(self, parent, kind, text):
        super().__init__(parent)
        self.withdraw()
        self.kind, self.result = kind, None
        self.title(T("dt_" + kind))
        self.transient(parent)
        self.resizable(False, False)
        ttk.Label(self, text=T("dh_" + kind), justify="left").pack(padx=14, pady=(14, 6), anchor="w")
        single = kind in ("input", "decision", "loop")
        self.box = tk.Text(self, width=50, height=2 if single else 5, font="TkFixedFont",
                           undo=True, bd=2, relief="groove")
        self.box.pack(padx=14)
        self.box.insert("1.0", text)
        self.box.focus_set()
        self.err = ttk.Label(self, foreground="#c62828", wraplength=420, justify="left")
        self.err.pack(padx=14, pady=3, anchor="w")
        row = ttk.Frame(self)
        row.pack(pady=(2, 12))
        ttk.Button(row, text=T("btn_ok"), command=self.ok).pack(side="left", padx=4)
        ttk.Button(row, text=T("btn_cancel"), command=self.destroy).pack(side="left", padx=4)
        self.bind("<Control-Return>", lambda e: self.ok())
        self.bind("<Escape>", lambda e: self.destroy())
        if single:
            self.box.bind("<Return>", lambda e: (self.ok(), "break")[1])
        center_window(self, parent)
        self.deiconify()
        self.wait_visibility()
        self.grab_set()

    def ok(self):
        text = self.box.get("1.0", "end").strip()
        err = check_text(self.kind, text)
        if err:
            self.err.config(text=err)
            return
        self.result = text
        self.destroy()


class InputDialog(tk.Toplevel):
    def __init__(self, parent, name):
        super().__init__(parent)
        self.withdraw()
        self.result = None
        self.title(T("dt_enter"))
        self.transient(parent)
        self.resizable(False, False)
        ttk.Label(self, text=T("d_enter", name=name)).pack(padx=18, pady=(16, 6))
        self.var = tk.StringVar()
        entry = ttk.Entry(self, textvariable=self.var, width=34)
        entry.pack(padx=18)
        entry.focus_set()
        row = ttk.Frame(self)
        row.pack(pady=12)
        ttk.Button(row, text=T("btn_ok").split("  ")[0], command=self.ok).pack(side="left", padx=4)
        ttk.Button(row, text=T("btn_cancel"), command=self.destroy).pack(side="left", padx=4)
        self.bind("<Return>", lambda e: self.ok())
        self.bind("<Escape>", lambda e: self.destroy())
        center_window(self, parent)
        self.deiconify()
        self.wait_visibility()
        self.grab_set()

    def ok(self):
        self.result = self.var.get()
        self.destroy()


def ask_text(parent, kind, text):
    d = TextDialog(parent, kind, text)
    parent.wait_window(d)
    return d.result


# ======================================================================
#  Main application
# ======================================================================
class App(tk.Tk):
    def __init__(self, path=None):
        super().__init__()
        self.title(APP)
        sw, sh = self.winfo_screenwidth(), self.winfo_screenheight()
        w, h = min(1280, sw - 40), min(780, sh - 90)
        self.geometry(f"{w}x{h}+{(sw - w) // 2}+{max(0, (sh - h) // 3)}")
        self.minsize(min(820, w), min(520, h))
        try:
            self.attributes("-zoomed", True)  # start maximised so nothing runs off the screen
        except tk.TclError:
            pass
        ttk.Style(self).theme_use("clam")
        base = tkfont.nametofont("TkDefaultFont")
        self.mfont = base.copy()
        self.mfont.configure(size=10)            # fixed font used only to measure text
        self.zfont = base.copy()
        self.zfont_b = base.copy()
        self.zfont_b.configure(weight="bold")
        self.hfont = base.copy()
        self.hfont.configure(size=9, weight="bold")
        self.zoom = 1.0
        self.update_fonts()

        self.nodes, self.edges, self.geo, self.edge_pts = {}, [], {}, {}
        self.next_id = 1
        self.region = (0, 0, 1000, 800)
        self.sel_node = self.sel_edge = self.link_src = self.hl = self.hl_err = None
        self.undo, self.redo = [], []
        self.path, self.dirty = None, False
        self.interp, self.mode, self.job, self.last_vars = None, "idle", None, {}
        self.drag = self.rb = None
        self.lines = 0
        self.tool = tk.StringVar(value="select")
        self.autolink = tk.BooleanVar(value=True)
        self.status = tk.StringVar()
        self.speed_value = 250
        self.zoom_var = tk.StringVar(value="100%")
        self.lang_var = tk.StringVar(value=LANG)
        self.build_ui()
        self.bind_keys()
        self.tool.trace_add("write", self.on_tool)
        self.protocol("WM_DELETE_WINDOW", self.quit_app)
        if path and os.path.exists(path):
            self.open_path(path)
        else:
            self.load_example("fact", force=True)
            self.say(T("st_welcome"))
        self.update_idletasks()
        self.after(150, self.center_view)

    # ----------------------------------------------------------------- UI
    def update_fonts(self):
        size = max(5, round(10 * self.zoom))
        self.zfont.configure(size=size)
        self.zfont_b.configure(size=size)

    def build_menu(self):
        menu = tk.Menu(self)
        self.config(menu=menu)
        f = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label=T("m_file"), menu=f)
        f.add_command(label=T("f_new"), accelerator="Ctrl+N", command=self.new)
        f.add_command(label=T("f_open"), accelerator="Ctrl+O", command=self.open_dialog)
        f.add_command(label=T("f_save"), accelerator="Ctrl+S", command=self.save)
        f.add_command(label=T("f_saveas"), command=self.save_as)
        ex = tk.Menu(f, tearoff=0)
        for eid in EXAMPLE_IDS:
            ex.add_command(label=T("ex_" + eid), command=lambda i=eid: self.load_example(i))
        f.add_cascade(label=T("f_example"), menu=ex)
        f.add_command(label=T("f_export"), command=self.export_ps)
        f.add_separator()
        f.add_command(label=T("f_quit"), command=self.quit_app)
        e = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label=T("m_edit"), menu=e)
        e.add_command(label=T("e_undo"), accelerator="Ctrl+Z", command=self.undo_cmd)
        e.add_command(label=T("e_redo"), accelerator="Ctrl+Y", command=self.redo_cmd)
        e.add_command(label=T("e_delete"), accelerator="Del", command=self.delete_sel)
        v = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label=T("m_view"), menu=v)
        v.add_command(label=T("v_in"), accelerator="Ctrl +", command=lambda: self.zoom_at(1.2))
        v.add_command(label=T("v_out"), accelerator="Ctrl -", command=lambda: self.zoom_at(1 / 1.2))
        v.add_command(label=T("v_reset"), accelerator="Ctrl 0", command=self.zoom_reset)
        v.add_command(label=T("v_fit"), command=self.fit_view)
        r = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label=T("m_run"), menu=r)
        r.add_command(label=T("r_run"), accelerator="F5", command=self.on_run)
        r.add_command(label=T("r_step"), accelerator="F6", command=self.on_step)
        r.add_command(label=T("r_stop"), accelerator="F8", command=self.on_stop)
        lg = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label=T("m_lang"), menu=lg)
        lg.add_radiobutton(label="Türkçe", value="tr", variable=self.lang_var,
                           command=lambda: self.set_lang("tr"))
        lg.add_radiobutton(label="English", value="en", variable=self.lang_var,
                           command=lambda: self.set_lang("en"))
        h = tk.Menu(menu, tearoff=0)
        menu.add_cascade(label=T("m_help"), menu=h)
        h.add_command(label=T("h_how"), command=self.show_help)

    def tool_button(self, parent, val):
        color = COLORS.get(val, "#e0e0e0")
        edge = OUTLINE.get(val, "#90a4ae")
        tk.Radiobutton(parent, text=T("t_" + val), value=val, variable=self.tool,
                       indicatoron=False, anchor="w", padx=10, pady=2, bg=color,
                       activebackground=shade(color, 0.93), selectcolor=shade(color, 0.78),
                       fg="#263238", relief="raised", bd=2, highlightthickness=2,
                       highlightbackground=edge, highlightcolor=edge
                       ).pack(fill="x", padx=8, pady=1)

    def build_sidebar(self):
        side = tk.Frame(self, bg=SIDE_BG, bd=1, relief="groove")
        side.pack(side="left", fill="y")

        def head(text):
            tk.Label(side, text=text, bg=SIDE_BG, fg="#546e7a", font=self.hfont,
                     anchor="w").pack(fill="x", padx=10, pady=(8, 1))

        head(T("s_tools"))
        for val in ("select", "connect"):
            self.tool_button(side, val)
        head(T("s_blocks"))
        for val in SIDE_BLOCKS:
            self.tool_button(side, val)
        head(T("s_edit"))
        row = tk.Frame(side, bg=SIDE_BG)
        row.pack(fill="x", padx=8)
        ttk.Button(row, text=T("b_undo"), command=self.undo_cmd).pack(fill="x", pady=1)
        ttk.Button(row, text=T("b_redo"), command=self.redo_cmd).pack(fill="x", pady=1)
        ttk.Button(row, text=T("b_delete"), command=self.delete_sel).pack(fill="x", pady=1)
        head(T("s_zoom"))
        zr = tk.Frame(side, bg=SIDE_BG)
        zr.pack(fill="x", padx=8)
        ttk.Button(zr, text="−", width=3, command=lambda: self.zoom_at(1 / 1.2)).pack(side="left")
        tk.Label(zr, textvariable=self.zoom_var, bg=SIDE_BG, width=5).pack(side="left", expand=True)
        ttk.Button(zr, text="+", width=3, command=lambda: self.zoom_at(1.2)).pack(side="right")
        ttk.Button(side, text=T("b_fit"), command=self.fit_view).pack(fill="x", padx=8, pady=(3, 8))

    def build_ui(self):
        self.build_menu()
        top = ttk.Frame(self, padding=(8, 5))
        top.pack(side="top", fill="x")
        ttk.Button(top, text=T("b_run"), command=self.on_run).pack(side="left", padx=2)
        ttk.Button(top, text=T("b_step"), command=self.on_step).pack(side="left", padx=2)
        ttk.Button(top, text=T("b_stop"), command=self.on_stop).pack(side="left", padx=2)
        ttk.Label(top, text=T("b_delay")).pack(side="left")
        self.speed = tk.Scale(top, from_=0, to=1000, resolution=50, orient="horizontal",
                              length=170, showvalue=True)
        self.speed.set(self.speed_value)
        self.speed.pack(side="left")
        ttk.Separator(top, orient="vertical").pack(side="left", fill="y", padx=12)
        ttk.Checkbutton(top, text=T("cb_auto"), variable=self.autolink).pack(side="left")

        ttk.Label(self, textvariable=self.status, relief="sunken", anchor="w",
                  padding=(8, 3)).pack(side="bottom", fill="x")
        self.build_sidebar()

        paned = ttk.PanedWindow(self, orient="horizontal")
        paned.pack(side="left", fill="both", expand=True)
        cf = tk.Frame(paned, bd=2, relief="sunken", bg="#90a4ae")
        paned.add(cf, weight=5)
        c = self.canvas = tk.Canvas(cf, bg="white", highlightthickness=0,
                                    xscrollincrement=20, yscrollincrement=20)
        sy = ttk.Scrollbar(cf, orient="vertical", command=c.yview)
        sx = ttk.Scrollbar(cf, orient="horizontal", command=c.xview)
        c.configure(yscrollcommand=sy.set, xscrollcommand=sx.set,
                    scrollregion=self.region)
        cf.grid_rowconfigure(0, weight=1)
        cf.grid_columnconfigure(0, weight=1)
        c.grid(row=0, column=0, sticky="nsew")
        sy.grid(row=0, column=1, sticky="ns")
        sx.grid(row=1, column=0, sticky="ew")

        right = ttk.PanedWindow(paned, orient="vertical")
        paned.add(right, weight=1)
        vf = ttk.LabelFrame(right, text=T("p_vars"))
        right.add(vf, weight=1)
        self.vtree = ttk.Treeview(vf, columns=("name", "value"), show="headings", height=8)
        self.vtree.heading("name", text=T("col_name"))
        self.vtree.heading("value", text=T("col_val"))
        self.vtree.column("name", width=80, anchor="w")
        self.vtree.column("value", width=150, anchor="w")
        self.vtree.pack(fill="both", expand=True, padx=3, pady=3)
        of = ttk.LabelFrame(right, text=T("p_out"))
        right.add(of, weight=2)
        self.console = tk.Text(of, width=30, height=12, font="TkFixedFont", state="disabled",
                               wrap="word", bg="#fafafa")
        cs = ttk.Scrollbar(of, command=self.console.yview)
        self.console.config(yscrollcommand=cs.set)
        ttk.Button(of, text=T("b_clear"), command=self.clear_console).pack(side="bottom", anchor="e", padx=3)
        cs.pack(side="right", fill="y")
        self.console.pack(fill="both", expand=True, padx=(3, 0), pady=3)
        self.console.tag_configure("err", foreground="#b71c1c")

        c.bind("<Button-1>", self.on_press)
        c.bind("<B1-Motion>", self.on_motion)
        c.bind("<ButtonRelease-1>", self.on_release)
        c.bind("<Double-Button-1>", self.on_double)
        c.bind("<Button-3>", self.on_rpress)
        c.bind("<B3-Motion>", self.on_rmotion)
        c.bind("<ButtonRelease-3>", self.on_rrelease)
        c.bind("<Delete>", self.delete_sel)
        c.bind("<BackSpace>", self.delete_sel)
        c.bind("<Button-4>", lambda e: c.yview_scroll(-3, "units"))
        c.bind("<Button-5>", lambda e: c.yview_scroll(3, "units"))
        c.bind("<Shift-Button-4>", lambda e: c.xview_scroll(-3, "units"))
        c.bind("<Shift-Button-5>", lambda e: c.xview_scroll(3, "units"))
        c.bind("<Control-Button-4>", lambda e: self.zoom_at(1.15, e.x, e.y))
        c.bind("<Control-Button-5>", lambda e: self.zoom_at(1 / 1.15, e.x, e.y))
        c.bind("<MouseWheel>", lambda e: self.zoom_at(1.15 if e.delta > 0 else 1 / 1.15, e.x, e.y)
               if e.state & 4 else c.yview_scroll(-1 if e.delta > 0 else 1, "units"))

    def bind_keys(self):
        self.bind("<Control-n>", lambda e: self.new())
        self.bind("<Control-o>", lambda e: self.open_dialog())
        self.bind("<Control-s>", lambda e: self.save())
        self.bind("<Control-z>", self.undo_cmd)
        self.bind("<Control-y>", self.redo_cmd)
        for k in ("<Control-plus>", "<Control-equal>", "<Control-KP_Add>"):
            self.bind(k, lambda e: self.zoom_at(1.2))
        for k in ("<Control-minus>", "<Control-KP_Subtract>"):
            self.bind(k, lambda e: self.zoom_at(1 / 1.2))
        self.bind("<Control-0>", lambda e: self.zoom_reset())
        self.bind("<F5>", lambda e: self.on_run())
        self.bind("<F6>", lambda e: self.on_step())
        self.bind("<F8>", lambda e: self.on_stop())
        self.bind("<Escape>", lambda e: self.tool.set("select"))

    def rebuild_ui(self):
        log = self.console.get("1.0", "end-1c")
        self.speed_value = self.speed.get()
        for w in self.winfo_children():
            w.destroy()
        self.build_ui()
        if log:
            self.console.config(state="normal")
            self.console.insert("end", log)
            self.console.config(state="disabled")
        self.refresh_vars()
        self.redraw()
        self.set_dirty(self.dirty)
        self.say(T("st_select"))
        self.after(60, self.center_view)

    def set_lang(self, code):
        global LANG
        if code == LANG:
            return
        LANG = code
        self.lang_var.set(code)
        save_config()
        self.after(20, self.rebuild_ui)  # let the menu finish closing first

    def say(self, msg):
        self.status.set(msg)

    def on_tool(self, *_):
        t = self.tool.get()
        self.set_link(None)
        if t in ("select", "connect"):
            self.say(T("st_" + t))
        else:
            self.say(T("st_place", name=T("t_" + t)))

    def show_help(self):
        w = tk.Toplevel(self)
        w.withdraw()
        w.title(T("help_title"))
        t = tk.Text(w, width=92, height=min(36, max(12, (self.winfo_height() - 80) // 18)),
                    font="TkFixedFont", wrap="none", padx=10, pady=8)
        sb = ttk.Scrollbar(w, command=t.yview)
        t.config(yscrollcommand=sb.set)
        t.insert("1.0", L(HELP_TR, HELP_EN))
        t.config(state="disabled")
        sb.pack(side="right", fill="y")
        t.pack(side="left", fill="both", expand=True)
        center_window(w, self)
        w.deiconify()

    def set_dirty(self, v=True):
        self.dirty = v
        name = os.path.basename(self.path) if self.path else T("untitled")
        self.title(f"{name}{'*' if v else ''} - {APP}")

    # ------------------------------------------------------------ drawing
    def disp(self, n):
        t = n["type"]
        if t == "start":
            return T("start_txt")
        if t == "end":
            return T("end_txt")
        pre = T("pre_" + t) if t in ("input", "output", "loop") else ""
        return pre + n["text"]

    def geom(self, n):
        """Block size in chart units (independent of zoom)."""
        t = n["type"]
        bw, bh = BASE[t]
        lines = self.disp(n).split("\n")
        tw = max(self.mfont.measure(s) for s in lines)
        lh = self.mfont.metrics("linespace")
        if t == "decision":
            return min(460, max(bw, tw * 1.7 + 30)), max(bh, len(lines) * lh * 1.8 + 24)
        return min(420, max(bw, tw + 46)), max(bh, len(lines) * lh + 26)

    def shape(self, t, x, y, w, h, **kw):
        c, z = self.canvas, self.zoom
        if t in ("start", "end"):
            return c.create_oval(x - w / 2, y - h / 2, x + w / 2, y + h / 2, **kw)
        if t in ("input", "output"):
            s = 16 * z
            return c.create_polygon(x - w / 2 + s, y - h / 2, x + w / 2, y - h / 2,
                                    x + w / 2 - s, y + h / 2, x - w / 2, y + h / 2, **kw)
        if t == "process":
            return c.create_rectangle(x - w / 2, y - h / 2, x + w / 2, y + h / 2, **kw)
        if t == "loop":
            s = 20 * z
            return c.create_polygon(x - w / 2 + s, y - h / 2, x + w / 2 - s, y - h / 2,
                                    x + w / 2, y, x + w / 2 - s, y + h / 2,
                                    x - w / 2 + s, y + h / 2, x - w / 2, y, **kw)
        return c.create_polygon(x, y - h / 2, x + w / 2, y, x, y + h / 2, x - w / 2, y, **kw)

    def draw_node(self, n):
        c, nid, t, z = self.canvas, n["id"], n["type"], self.zoom
        w, h = self.geo[nid] = self.geom(n)
        x, y, W, H = n["x"] * z, n["y"] * z, w * z, h * z
        off = max(2, 4 * z)
        self.shape(t, x + off, y + off, W, H, fill="#cfd8dc", outline="",
                   tags=("shadow", f"n{nid}"))
        self.shape(t, x, y, W, H, fill=COLORS[t], outline=OUTLINE[t],
                   width=max(1.5, 2.6 * z), tags=("node", f"n{nid}", f"s{nid}"))
        c.create_text(x, y, text=self.disp(n), font=self.zfont, justify="center", fill="#263238",
                      width=(0.62 * W if t == "decision" else W - 30 * z), tags=("node", f"n{nid}"))

    def anchors(self, nid):
        n = self.nodes[nid]
        w, h = self.geo[nid]
        x, y = n["x"], n["y"]
        sk = 8 if n["type"] in ("input", "output") else 0
        return {"t": (x, y - h / 2), "b": (x, y + h / 2),
                "l": (x - w / 2 + sk, y), "r": (x + w / 2 - sk, y)}

    def is_back(self, e):
        return self.nodes[e["dst"]]["y"] < self.nodes[e["src"]]["y"] - 5

    def edge_points(self, e):
        """Arrow route in chart units."""
        a, b = self.nodes[e["src"]], self.nodes[e["dst"]]
        A, B = self.anchors(a["id"]), self.anchors(b["id"])
        if self.is_back(e):  # going back up (a loop): swing round the left side
            k = 0
            for o in self.edges:
                if o is e:
                    break
                if o["dst"] == e["dst"] and self.is_back(o):
                    k += 1
            p, q = A["l"], B["l"]
            mx = min(p[0], q[0]) - 35 - 16 * k
            return [p, (mx, p[1]), (mx, q[1]), q]
        _, i, j = min((math.dist(A[i], B[j]), i, j) for i in A for j in B)
        return [A[i], B[j]]

    def draw_edges(self):
        c, z = self.canvas, self.zoom
        c.delete("edge")
        self.edge_pts = {}
        if self.sel_edge not in {(e["src"], e["dst"]) for e in self.edges}:
            self.sel_edge = None
        for e in self.edges:
            key = (e["src"], e["dst"])
            pts = self.edge_pts[key] = self.edge_points(e)
            sel = key == self.sel_edge
            c.create_line(*[v * z for p in pts for v in p], arrow="last",
                          arrowshape=(11 * z, 13 * z, 5 * z), width=max(1.5, (3.2 if sel else 2.2) * z),
                          fill="#1565c0" if sel else "#37474f", joinstyle="round", tags="edge")
            if e["label"]:
                (x0, y0), (x1, y1) = pts[0], pts[1]
                d = math.hypot(x1 - x0, y1 - y0) or 1
                ux, uy = (x1 - x0) / d, (y1 - y0) / d
                sg = 1 if e["label"] in ("Yes", "Loop") else -1
                c.create_text((x0 + ux * 24 - uy * 14 * sg) * z, (y0 + uy * 24 + ux * 14 * sg) * z,
                              text=T("lbl_" + e["label"]), font=self.zfont_b, tags="edge",
                              fill=LABEL_COLOR.get(e["label"], "#37474f"))
        try:
            c.tag_lower("edge")
            c.tag_raise("edge", "shadow")
        except tk.TclError:
            pass

    def draw_halo(self):
        c, z = self.canvas, self.zoom
        c.delete("halo")
        nid = self.sel_node
        if nid in self.nodes and nid in self.geo:
            n, (w, h) = self.nodes[nid], self.geo[nid]
            pad = 8
            c.create_rectangle(n["x"] * z - w * z / 2 - pad, n["y"] * z - h * z / 2 - pad,
                               n["x"] * z + w * z / 2 + pad, n["y"] * z + h * z / 2 + pad,
                               outline="#1565c0", dash=(5, 3), width=2, tags="halo")

    def update_region(self):
        c = self.canvas
        bb = c.bbox("all") or (0, 0, 0, 0)
        vw, vh = max(c.winfo_width(), 300), max(c.winfo_height(), 200)
        self.region = (bb[0] - vw, bb[1] - vh, bb[2] + vw, bb[3] + vh)
        c.configure(scrollregion=self.region)

    def redraw(self):
        self.canvas.delete("all")
        self.geo = {}
        for n in self.nodes.values():
            self.draw_node(n)
        self.draw_edges()
        for nid in self.nodes:
            self.style(nid)
        self.draw_halo()
        self.update_region()

    def style(self, nid):
        if nid not in self.nodes:
            return
        t, z = self.nodes[nid]["type"], self.zoom
        fill, outline, width = COLORS[t], OUTLINE[t], max(1.5, 2.6 * z)
        if nid == self.link_src:
            outline, width = "#2e7d32", max(3, 5 * z)
        if nid == self.hl:
            outline, width, fill = "#ef6c00", max(3, 5 * z), "#ffe082"
        if nid == self.hl_err:
            outline, width, fill = "#b71c1c", max(3, 5 * z), "#ef9a9a"
        self.canvas.itemconfig(f"s{nid}", fill=fill, outline=outline, width=width)

    def set_hl(self, nid, err=False):
        old = (self.hl, self.hl_err)
        self.hl, self.hl_err = (None, nid) if err else (nid, None)
        for i in old + (nid,):
            self.style(i)
        if nid in self.nodes:
            n = self.nodes[nid]
            self.keep_visible(n["x"], n["y"])

    # --------------------------------------------------------- view / zoom
    def keep_visible(self, x, y):
        c, z = self.canvas, self.zoom
        cx, cy = x * z, y * z
        vx0, vy0 = c.canvasx(0), c.canvasy(0)
        vw, vh = c.winfo_width(), c.winfo_height()
        if not (vx0 + 50 < cx < vx0 + vw - 50 and vy0 + 50 < cy < vy0 + vh - 50):
            self.scroll_to(x, y, vw / 2, vh / 2)

    def scroll_to(self, mx, my, sx, sy):
        """Scroll so that chart point (mx, my) appears at screen position (sx, sy)."""
        x0, y0, x1, y1 = self.region
        z = self.zoom
        self.canvas.xview_moveto((mx * z - sx - x0) / (x1 - x0))
        self.canvas.yview_moveto((my * z - sy - y0) / (y1 - y0))

    def set_zoom(self, z):
        self.zoom = max(0.25, min(3.0, z))
        self.update_fonts()
        self.zoom_var.set(f"{round(self.zoom * 100)}%")
        self.redraw()

    def zoom_at(self, factor, sx=None, sy=None):
        c = self.canvas
        if sx is None:
            sx, sy = c.winfo_width() / 2, c.winfo_height() / 2
        mx, my = c.canvasx(sx) / self.zoom, c.canvasy(sy) / self.zoom
        self.set_zoom(self.zoom * factor)
        self.scroll_to(mx, my, sx, sy)

    def zoom_reset(self):
        self.zoom_at(1 / self.zoom)

    def center_view(self):
        c = self.canvas
        c.update_idletasks()
        self.update_region()
        bb = c.bbox("all")
        if not bb:
            return
        vw, vh = c.winfo_width(), c.winfo_height()
        z = self.zoom
        cx = (bb[0] + bb[2]) / 2 if bb[2] - bb[0] < vw - 60 else bb[0] - 30 + vw / 2
        cy = (bb[1] + bb[3]) / 2 if bb[3] - bb[1] < vh - 60 else bb[1] - 30 + vh / 2
        self.scroll_to(cx / z, cy / z, vw / 2, vh / 2)

    def fit_view(self):
        c = self.canvas
        bb = c.bbox("node")
        if not bb:
            return
        vw, vh = max(c.winfo_width(), 200), max(c.winfo_height(), 200)
        bw, bh = (bb[2] - bb[0]) / self.zoom, (bb[3] - bb[1]) / self.zoom
        self.set_zoom(min((vw - 80) / max(bw, 1), (vh - 80) / max(bh, 1), 1.5))
        self.center_view()

    # --------------------------------------------------------- selection
    def select(self, nid=None, edge=None):
        old = self.sel_node
        self.sel_node, self.sel_edge = nid, edge
        self.style(old)
        self.style(nid)
        self.draw_edges()
        self.draw_halo()

    def set_link(self, nid):
        old, self.link_src = self.link_src, nid
        self.style(old)
        self.style(nid)
        if nid:
            self.say(T("st_link"))

    # --------------------------------------------------------- hit tests
    def node_at(self, x, y):
        for n in reversed(list(self.nodes.values())):
            w, h = self.geo.get(n["id"], (0, 0))
            if abs(x - n["x"]) <= w / 2 and abs(y - n["y"]) <= h / 2:
                return n["id"]
        return None

    def edge_at(self, x, y):
        for key, pts in self.edge_pts.items():
            for (x0, y0), (x1, y1) in zip(pts, pts[1:]):
                if seg_dist(x, y, x0, y0, x1, y1) < 7 / self.zoom:
                    return key
        return None

    def cxy(self, ev):
        """Mouse position in chart units."""
        return self.canvas.canvasx(ev.x) / self.zoom, self.canvas.canvasy(ev.y) / self.zoom

    # ------------------------------------------------------ mouse events
    def on_press(self, ev):
        self.canvas.focus_set()
        x, y = self.cxy(ev)
        tool, nid = self.tool.get(), self.node_at(x, y)
        self.drag = None
        if tool in PLACE:
            self.place(tool, round(x / GRID) * GRID, round(y / GRID) * GRID)
        elif tool == "connect":
            if nid is None:
                self.set_link(None)
            elif self.link_src is None:
                self.set_link(nid)
            else:
                src = self.link_src
                self.set_link(None)
                self.connect(src, nid)
        elif nid is not None:
            self.select(nid=nid)
            n = self.nodes[nid]
            self.drag = {"id": nid, "dx": n["x"] - x, "dy": n["y"] - y, "moved": False}
        else:
            key = self.edge_at(x, y)
            self.select(edge=key)
            if key is None:
                self.canvas.scan_mark(ev.x, ev.y)
                self.drag = {"pan": True}

    def on_motion(self, ev):
        d = self.drag
        if not d:
            return
        if d.get("pan"):
            self.canvas.scan_dragto(ev.x, ev.y, gain=1)
            return
        x, y = self.cxy(ev)
        n = self.nodes[d["id"]]
        nx = round((x + d["dx"]) / GRID) * GRID
        ny = round((y + d["dy"]) / GRID) * GRID
        if nx == n["x"] and ny == n["y"]:
            return
        if not d["moved"]:
            self.checkpoint()
            d["moved"] = True
        self.canvas.move(f"n{n['id']}", (nx - n["x"]) * self.zoom, (ny - n["y"]) * self.zoom)
        n["x"], n["y"] = nx, ny
        self.draw_edges()
        self.draw_halo()

    def on_release(self, ev):
        if self.drag and self.drag.get("moved"):
            self.update_region()
        self.drag = None

    def on_double(self, ev):
        x, y = self.cxy(ev)
        nid = self.node_at(x, y)
        if nid is not None:
            self.edit_node(nid)
            return
        key = self.edge_at(x, y)
        if key:
            self.flip_label(key)

    def on_rpress(self, ev):
        x, y = self.canvas.canvasx(ev.x), self.canvas.canvasy(ev.y)
        nid = self.node_at(x / self.zoom, y / self.zoom)
        self.rb = None
        if nid is not None:
            line = self.canvas.create_line(x, y, x, y, dash=(4, 3), width=2,
                                           fill="#2e7d32", arrow="last")
            self.rb = {"src": nid, "line": line}

    def on_rmotion(self, ev):
        if self.rb:
            n, z = self.nodes[self.rb["src"]], self.zoom
            self.canvas.coords(self.rb["line"], n["x"] * z, n["y"] * z,
                               self.canvas.canvasx(ev.x), self.canvas.canvasy(ev.y))

    def on_rrelease(self, ev):
        if not self.rb:
            return
        x, y = self.cxy(ev)
        self.canvas.delete(self.rb["line"])
        src, self.rb = self.rb["src"], None
        dst = self.node_at(x, y)
        if dst is not None and dst != src:
            self.connect(src, dst)

    # --------------------------------------------------- chart editing
    def new_id(self):
        self.next_id += 1
        return self.next_id - 1

    def to_json(self):
        return json.dumps({"version": 2, "nodes": list(self.nodes.values()),
                           "edges": self.edges}, indent=1, ensure_ascii=False)

    def load_dict(self, d):
        self.nodes = {n["id"]: n for n in d["nodes"]}
        self.edges = d["edges"]
        self.sel_node = self.sel_edge = self.link_src = self.hl = self.hl_err = None
        self.next_id = max(self.nodes, default=0) + 1
        self.redraw()

    def checkpoint(self, snap=None):
        self.undo.append(snap or self.to_json())
        del self.undo[:-100]
        self.redo.clear()
        self.set_dirty(True)

    def undo_cmd(self, ev=None):
        if self.undo:
            self.redo.append(self.to_json())
            self.load_dict(json.loads(self.undo.pop()))
            self.set_dirty(True)

    def redo_cmd(self, ev=None):
        if self.redo:
            self.undo.append(self.to_json())
            self.load_dict(json.loads(self.redo.pop()))
            self.set_dirty(True)

    def link(self, src, dst):
        """Add an arrow. Returns an error message, or None on success."""
        s, d = self.nodes[src], self.nodes[dst]
        if src == dst:
            return T("er_self")
        if s["type"] == "end":
            return T("er_end")
        if d["type"] == "start":
            return T("er_start")
        if any(e["src"] == src and e["dst"] == dst for e in self.edges):
            return T("er_dup")
        outs = [e for e in self.edges if e["src"] == src]
        label = ""
        if s["type"] in PAIR:
            first, second = PAIR[s["type"]]
            if len(outs) >= 2:
                return T("er_full_" + s["type"])
            label = first if first not in {e["label"] for e in outs} else second
        else:  # one arrow out: a new one replaces the old
            self.edges = [e for e in self.edges if e["src"] != src]
        self.edges.append({"src": src, "dst": dst, "label": label})
        return None

    def connect(self, src, dst):
        snap = self.to_json()
        err = self.link(src, dst)
        if err:
            self.say(err)
            return
        self.checkpoint(snap)
        self.draw_edges()

    def place(self, kind, x, y):
        self.tool.set("select")
        if kind == "start" and any(n["type"] == "start" for n in self.nodes.values()):
            self.say(T("er_one_start"))
            return
        text = {"start": "Start", "end": "End"}.get(kind)
        if text is None:
            text = ask_text(self, kind, "")
            if text is None:
                return
        snap = self.to_json()
        nid = self.new_id()
        self.nodes[nid] = {"id": nid, "type": kind, "text": text, "x": x, "y": y}
        if self.autolink.get() and self.sel_node in self.nodes and kind != "start":
            self.link(self.sel_node, nid)
        self.checkpoint(snap)
        self.sel_node, self.sel_edge = nid, None
        self.redraw()

    def edit_node(self, nid):
        n = self.nodes[nid]
        if n["type"] in ("start", "end"):
            return
        text = ask_text(self, n["type"], n["text"])
        if text is None or text == n["text"]:
            return
        self.checkpoint()
        n["text"] = text
        self.redraw()

    def flip_label(self, key):
        e = next(e for e in self.edges if (e["src"], e["dst"]) == key)
        kind = self.nodes[e["src"]]["type"]
        if kind not in PAIR:
            return
        self.checkpoint()
        first, second = PAIR[kind]
        new = second if e["label"] == first else first
        for o in self.edges:
            if o is not e and o["src"] == e["src"] and o["label"] == new:
                o["label"] = e["label"]
        e["label"] = new
        self.draw_edges()

    def delete_sel(self, ev=None):
        snap = self.to_json()
        if self.sel_node in self.nodes:
            nid = self.sel_node
            del self.nodes[nid]
            self.edges = [e for e in self.edges if nid not in (e["src"], e["dst"])]
            self.sel_node = None
        elif self.sel_edge:
            self.edges = [e for e in self.edges if (e["src"], e["dst"]) != self.sel_edge]
            self.sel_edge = None
        else:
            return
        self.checkpoint(snap)
        self.redraw()

    # -------------------------------------------------------- file I/O
    def filetypes(self):
        return [(T("ft_flow"), "*" + EXT), (T("ft_all"), "*")]

    def confirm_discard(self):
        if not self.dirty:
            return True
        r = messagebox.askyesnocancel(APP, T("ask_save"), parent=self)
        if r is None:
            return False
        return self.save() if r else True

    def reset_doc(self, path=None):
        self.undo.clear()
        self.redo.clear()
        self.path = path
        self.set_dirty(False)
        self.clear_console()
        self.last_vars = {}
        self.refresh_vars()

    def new(self):
        if not self.confirm_discard():
            return
        self.on_stop()
        self.load_dict({"nodes": [{"id": 1, "type": "start", "text": "Start", "x": 260, "y": 60}],
                        "edges": []})
        self.reset_doc()
        self.select(nid=1)  # so the first block you place links from Start
        self.say(T("st_new"))
        self.after(30, self.center_view)

    def load_example(self, eid, force=False):
        if not force and not self.confirm_discard():
            return
        self.on_stop()
        nodes, edges = example(eid)
        self.load_dict({"nodes": nodes, "edges": edges})
        self.reset_doc()
        self.after(30, self.center_view)

    def open_dialog(self):
        if not self.confirm_discard():
            return
        p = filedialog.askopenfilename(parent=self, filetypes=self.filetypes())
        if p:
            self.open_path(p)

    def open_path(self, p):
        try:
            with open(p, encoding="utf-8") as fh:
                d = json.load(fh)
            validate_chart(d)
        except (OSError, ValueError, KeyError, TypeError):
            messagebox.showerror(APP, T("bad_file"), parent=self)
            return
        self.on_stop()
        self.load_dict(d)
        self.reset_doc(p)
        self.say(T("st_opened", path=p))
        self.after(30, self.center_view)

    def save(self):
        return self.write_to(self.path) if self.path else self.save_as()

    def save_as(self):
        p = filedialog.asksaveasfilename(parent=self, defaultextension=EXT,
                                         filetypes=self.filetypes())
        return self.write_to(p) if p else False

    def write_to(self, p):
        try:
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(self.to_json())
        except OSError as e:
            messagebox.showerror(APP, T("save_err", err=e), parent=self)
            return False
        self.path = p
        self.set_dirty(False)
        self.say(T("st_saved", path=p))
        return True

    def export_ps(self):
        box = self.canvas.bbox("node")
        if not box:
            return
        p = filedialog.asksaveasfilename(parent=self, defaultextension=".ps",
                                         filetypes=[("PostScript", "*.ps")])
        if p:
            self.canvas.delete("halo")
            self.canvas.postscript(file=p, colormode="color", x=box[0] - 20, y=box[1] - 20,
                                   width=box[2] - box[0] + 40, height=box[3] - box[1] + 40)
            self.draw_halo()
            self.say(T("st_exported", path=p, name=os.path.basename(p)))

    def quit_app(self):
        if self.confirm_discard():
            self.cancel_job()
            self.destroy()

    # --------------------------------------------------------- running
    def clear_console(self):
        self.console.config(state="normal")
        self.console.delete("1.0", "end")
        self.console.config(state="disabled")
        self.lines = 0

    def emit(self, s, tag=None):
        c = self.console
        c.config(state="normal")
        c.insert("end", s + "\n", tag)
        self.lines += 1
        if self.lines > 3000:
            c.delete("1.0", "1001.0")
            self.lines -= 1000
        c.see("end")
        c.config(state="disabled")

    def refresh_vars(self):
        v = self.interp.vars if self.interp else self.last_vars
        self.vtree.delete(*self.vtree.get_children())
        for k in sorted(v):
            self.vtree.insert("", "end", values=(k, fmt(v[k])))

    def ask_input(self, name):
        d = InputDialog(self, name)
        self.wait_window(d)
        return d.result

    def cancel_job(self):
        if self.job:
            self.after_cancel(self.job)
            self.job = None

    def begin(self):
        for n in self.nodes.values():
            if n["type"] in ("start", "end"):
                continue
            err = check_text(n["type"], n["text"])
            if err:
                self.set_hl(n["id"], err=True)
                messagebox.showwarning(APP, T("fix_block", err=err), parent=self)
                return False
        try:
            self.interp = Interpreter(list(self.nodes.values()), self.edges,
                                      self.ask_input, self.emit)
        except FlowError as e:
            messagebox.showwarning(APP, str(e), parent=self)
            return False
        self.clear_console()
        self.last_vars = {}
        self.refresh_vars()
        self.set_hl(self.interp.cur)
        return True

    def finish(self):
        self.cancel_job()
        if self.interp:
            self.last_vars = self.interp.vars
            self.refresh_vars()
        self.interp, self.mode = None, "idle"

    def advance(self):
        """Run one block. Returns True if the run can continue."""
        it = self.interp
        try:
            st = it.step()
        except FlowError as e:
            nid = e.nid or it.cur
            self.finish()
            self.set_hl(nid, err=True)
            self.emit(T("ie_prefix", msg=e), "err")
            self.say(T("st_errstop"))
            return False
        if st == "ok":
            self.set_hl(it.cur)
            return True
        if st == "done":
            self.set_hl(it.cur)
            self.emit(T("msg_done"))
            self.say(T("st_finished", n=it.steps))
        else:
            self.say(T("st_cancel"))
        self.finish()
        return False

    def tick(self):
        self.job = None
        if self.mode != "auto" or not self.interp:
            return
        delay = int(self.speed.get())
        for _ in range(1 if delay else 300):
            if not self.advance():
                return
        self.refresh_vars()
        self.job = self.after(max(delay, 1), self.tick)

    def on_run(self):
        self.cancel_job()
        if self.interp is None and not self.begin():
            return
        self.mode = "auto"
        self.say(T("st_running"))
        self.tick()

    def on_step(self):
        self.cancel_job()
        if self.interp is None:
            if self.begin():
                self.mode = "paused"
                self.say(T("st_step"))
            return
        self.mode = "paused"
        if self.advance():
            self.refresh_vars()

    def on_stop(self):
        if self.interp is None:
            return
        self.finish()
        self.set_hl(None)
        self.say(T("st_stopped"))


if __name__ == "__main__":
    load_config()
    try:
        App(sys.argv[1] if len(sys.argv) > 1 else None).mainloop()
    except tk.TclError as err:
        sys.exit(f"Could not open a window: {err}")
