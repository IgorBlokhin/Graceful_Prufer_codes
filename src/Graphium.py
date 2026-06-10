from __future__ import annotations
import dearpygui.dearpygui as dpg
import Diktyonphi as phi
from paths import steps_dir, resource_path

# =========================================================
#                 INICIALIZACE A PÍSMO
# =========================================================

dpg.create_context()

def load_font():
    """
    Načte TTF a přidá rozsahy Unicode:
    - latinka
    - cyrilice
    - Latin Extended-A (č, ř, ě, š, ž, ů, …)
    """
    font_path = resource_path("assets/font/DejaVuSans.ttf")
    print("Font path:", font_path)
    print("Font exists:", font_path.exists())

    if not font_path.exists():
        print("[font] WARNING: font file not found, using default DearPyGui font.")
        return None

    try:
        with dpg.font_registry():
            with dpg.font(str(font_path), 18) as font:
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Default)
                dpg.add_font_range_hint(dpg.mvFontRangeHint_Cyrillic)
                dpg.add_font_range(0x0100, 0x017F)  # Latin Extended-A
        print("[font] Loaded font successfully.")
        return font
    except Exception as e:
        print(f"[font] ERROR: {e}")
        return None

# =========================================================
#                 ČTENÍ ZADANÝCH ВФЕ
# =========================================================

def parse_code(text: str):
    """'1 2 3', '1,2,3', '1; 2; 3' -> [1, 2, 3]."""
    for sep in [",", ";", ":", "\t"]:
        text = text.replace(sep, " ")
    return [int(x) for x in text.split() if x.strip()]

def parse_edges(text: str):
    """"'1 2 2 4', '1,2,2,4', '1;2;2;4' -> [(1, 2), (2, 4)]."""
    for sep in [",", ";", ":", "\t"]:
        text = text.replace(sep, " ")
    list_of_vertices = text.split()
    list_of_edges = []
    for i in range(len(list_of_vertices)):
        if i % 2 == 0:
            list_of_edges.append((int(list_of_vertices[i]), int(list_of_vertices[i + 1])))
    return list_of_edges

# =========================================================
#                       JAZYKY
# =========================================================

TRANSLATIONS = {
    "cs": {
        "main_window": "Hlavní okno",
        "lang_label": "Jazyk:",
        "lang_items": ["Čeština", "Русский", "English"],
        "prufer_tab": "Prüferův kód",
        "sheppard_tab": "Sheppardův kód",
        "from_prufer_to_graph": "Graf z kódu",
        "from_sheppard_to_graph": "Graf z kódu",
        "from_graph_to_sheppard": "Kód z grafu",
        "from_graph_to_prufer": "Kód z grafu",
        "space_tab": "Prostor Prüferových kódů",
        "prufer_input_label": "Zadejte Prüferův kód (hodnoty musí být od 0 do n-1 a délka kódu n-2):",
        "prufer_button": "Zobrazit strom",
        "prufer_hint": "Výsledný strom se zobrazí níže.",
        "code_hint": "Výsledný kód se zobrazí níže.",
        "prufer_code_announcment_label": "Prüferův kód:",
        "sheppard_code_announcment_label": "Sheppardův kód:",
        "show_code_button": "Ukazat kód",
        "prufer_error_invalid": "Neplatný Prüferův kód.",
        "prufer_error_export": "Chyba při generování obrázku stromu.",
        "tree_input_label": "Zadejte hrany stromu:",
        "graph_input_label": "Zadejte hrany graphu:",
        "show_sheppard_code_button": "Ukazat kód",
        "show_prufer_code_button": "Ukazat kód",
        "show_steps": "Zobrazit kroky",
        "choose_step": "Vyberte krok: ",
        "sheppard_input_label": "Zadejte Sheppardův kód:",
        "sheppard_button": "Zobrazit graf",
        "sheppard_hint": "Výsledný graf se zobrazí níže.",
        "sheppard_error_invalid": "Neplatný Sheppardův kód.",
        "sheppard_error_export": "Chyba při generování obrázku stromu.",
        "graceful_error": "Ohodnocení není graciózní, proto pro něj neexistuje Sheppardův kód.",
        "not_tree_error": "Graf, který jste zadal, není stromem, proto pro něj neexistuje žádný Prüferův kód.",
        "prufer_error": """Neplatný Prüferův kód.

Zadaný kód porušuje základní pravidla platnosti:
1. Všechny hodnoty musí být celá nezáporná čísla (0, 1, 2, ...).
2. Pokud délka kódu je n, maximální číslo v kódu je n+1.
""",
        "bad_labeling_tree": "Prüferův kód neexistuje. Ohodnocení vrcholů musejí být z množiny {0, ..., n-1}.",
        "sheppard_error": """Neplatný Sheppardův kód.

Zadaný kód nebo kód ze zadaného grafu porušuje základní pravidla platnosti:
1. Všechny hodnoty musí být celá nezáporná čísla (0, 1, 2, ...).
2. Na žádné pozici nesmí být číslo větší než počet prvků napravo od této pozice.
3. Ohodnocení vrcholů musí být zvoleno z množiny {0, 1, ..., m}, kde m je počet hran grafu.
Z toho plyne:
Na poslední pozici může být pouze 0.
Na předposlední pozici pouze 0 nebo 1.
Na třetí pozici od konce pouze 0, 1 nebo 2, atd.
Obecně: na pozici i může být jen číslo z intervalu 0 až n - i, kde n je délka kódu.
Pokud je některé číslo mimo tento povolený rozsah, kód požaduje neexistující volbu a nelze jej dekódovat.
Zkontrolujte prosím zadaný kód nebo graf a opravte neplatné hodnoty.""",
    },
    "ru": {
        "main_window": "Главное окно",
        "lang_label": "Язык:",
        "lang_items": ["Čeština", "Русский", "English"],
        "prufer_tab": "Код Прюфера",
        "sheppard_tab": "Код Шеппарда",
        "from_prufer_to_graph": "Граф по коду",
        "from_sheppard_to_graph": "Граф по коду",
        "from_graph_to_sheppard": "Кoд по графу",
        "from_graph_to_prufer": "Кoд по графу",
        "space_tab": "Пространство Прюфера",
        "prufer_input_label": "Введите код Прюфера (значения от 0 до n-1 при длине кода n-2):",
        "prufer_button": "Показать дерево",
        "prufer_hint": "Изображение дерева появится ниже.",
        "code_hint": "Код появится ниже.",
        "prufer_code_announcment_label": "Код Прюфера:",
        "sheppard_code_announcment_label": "Код Шеппарда:",
        "tree_input_label": "Задайте peбpa дерева:",
        "graph_input_label": "Задайте ребра графа:",
        "show_sheppard_code_button": "Показать код",
        "show_prufer_code_button": "Показать код",
        "prufer_error_invalid": "Некорректный код Прюфера.",
        "prufer_error_export": "Ошибка при создании изображения дерева.",
        "show_steps": "Показать шаги",
        "choose_step": "Выберите шаг: ",
        "sheppard_input_label": "Введите код Шеппарда:",
        "sheppard_button": "Показать граф",
        "sheppard_hint": "Изображение графа появится ниже.",
        "graceful_error": "Введенная разметка не является грациозной, поэтому нельзя найти ее код Шеппарда.",
        "not_tree_error": "Введенный граф не является деревом, поэтому нельзя найти его код Прюфера.",
        "sheppard_error_invalid": "Некорректный код Шеппарда.",
        "sheppard_error_export": "Ошибка при создании изображения дерева.",
        "prufer_error": """Недопустимый код Прюфера.

Введенный код нарушает основные правила допустимости:
1. Все значения должны быть целыми неотрицательными числами (0, 1, 2, ...).
2. Если длина кода n, максимальное число в коде n+1.
""",
        "bad_labeling_tree": "Код Прюфера не существует. Вершины должны быть размечены числами из множества {0, ..., n-1}.",
        "sheppard_error": """Недопустимый код Шеппарда.

Введенный код или код, полученный из введенного графа, нарушает основные правила допустимости:
1. Все значения должны быть целыми неотрицательными числами (0, 1, 2, ...).
2. Ни в одной позиции число не может быть больше, чем количество элементов справа от этой позиции.
3. Максимальная метка вершины не должна быть больше чем число ребер в графе.
Из этого следует:
На последней позиции может быть только 0.
На предпоследней позиции может быть только 0 или 1.
На третьей позиции от конца может быть только 0, 1 или 2 и т. д.
В общем случае: на позиции i может быть только число из интервала от 0 до n - i, где n — длина кода.
Если какое-либо число выходит за пределы этого допустимого диапазона, код требует несуществующего выбора и не может быть декодирован.
Пожалуйста, проверьте введенный код или граф и исправьте недопустимые значения.""",
    },
    "en": {
        "main_window": "Main window",
        "lang_label": "Language:",
        "lang_items": ["Čeština", "Русский", "English"],
        "prufer_tab": "Prüfer code",
        "sheppard_tab": "Sheppard code",
        "from_prufer_to_graph": "Graph from code",
        "from_sheppard_to_graph": "Graph from code",
        "from_graph_to_sheppard": "Code from graph",
        "from_graph_to_prufer": "Code from graph",
        "tab_space": "Prüfer space",
        "prufer_input_label": "Enter Prüfer code (values must be from 0 to n-1 and the length of the code n-2):",
        "prufer_button": "Show tree",
        "tree_input_label": "Set tree edges:",
        "show_sheppard_code_button": "Show code",
        "show_prufer_code_button": "Show code",
        "graph_input_label": "Set graph edges:",
        "prufer_hint": "The tree image will appear below.",
        "code_hint": "The code will appear below.",
        "prufer_error_invalid": "Invalid Prüfer code.",
        "prufer_error_export": "Failed to generate tree image.",
        "prufer_code_announcment_label": "The Prüfer code is:",
        "sheppard_code_announcment_label": "The Sheppard code is:",
        "not_tree_error": "The graph you have entered is not a tree, so there is no Prüfer code for it.",
        "graceful_error": "The labeling you have entered is not graceful, so there is no Sheppard code for it.",
        "show_steps": "Show steps",
        "choose_step": "Choose step: ",
        "sheppard_input_label": "Enter Sheppard code:",
        "sheppard_button": "Show graph",
        "sheppard_hint": "The graph image will appear below.",
        "sheppard_error_invalid": "Invalid Sheppard code.",
        "sheppard_error_export": "Failed to generate tree image.",
        "bad_labeling_tree": "The Prüfer code doesn't exist. Vertex labelings must be from the set {0, ..., n-1}.",
        "prufer_error": """Invalid Prufer code.

The entered code violates the Basic Rules of validity:
1. All values must be non-negative integers (0, 1, 2, ...).
2. If the length of the code is n, the maximum number in the code is n+1.
""",
        "sheppard_error": """Invalid Sheppard code.

The entered code or the code from the entered graph violates the basic rules of validity:
1. All values must be non-negative integers (0, 1, 2, ...).
2. No position may contain a number greater than the number of elements to the right of that position.
3. The vertex labels must be selected from the set {0, 1, ..., m}, where m denotes the number of edges of the graph.
It follows that:
The last position can only contain 0.
Only 0 or 1 can be in the penultimate position.
Only 0, 1, or 2 can be in the third position from the end, etc.
In general: only a number from the interval 0 to n - i can be in position i, where n is the length of the code.
If any number is outside this allowed range, the code requests a non-existent option and cannot be decoded.
Please check the entered code or graph and correct any invalid values.""",
    },
}

current_lang = "cs"
t = TRANSLATIONS[current_lang]

current_codes = {
    "prufer": {"code": None, "by_steps": None, "destination": None},
    "sheppard": {"code": None, "by_steps": None, "destination": None},
}

def apply_language(lang: str):
    global current_lang, t
    current_lang = lang
    t = TRANSLATIONS[lang]

    dpg.set_item_label("main_window", t["main_window"])

    dpg.set_value("lang_label_text", t["lang_label"])
    dpg.configure_item("lang_combo", items=t["lang_items"])

    if lang == "cs":
        dpg.set_value("lang_combo", "Čeština")
    elif lang == "ru":
        dpg.set_value("lang_combo", "Русский")
    else:
        dpg.set_value("lang_combo", "English")

    dpg.set_item_label("prufer_tab", t["prufer_tab"])
    dpg.set_item_label("sheppard_tab", t["sheppard_tab"])
    dpg.set_item_label("to_graph_sheppard", t["from_prufer_to_graph"])
    dpg.set_item_label("to_graph_prufer", t["from_sheppard_to_graph"])
    dpg.set_item_label("to_code_sheppard", t["from_graph_to_prufer"])
    dpg.set_item_label("to_code_prufer", t["from_graph_to_sheppard"])

    # Prüfer
    dpg.set_value("prufer_input_label", t["prufer_input_label"])
    dpg.set_item_label("prufer_button", t["prufer_button"])
    dpg.set_value("prufer_hint", t["prufer_hint"])
    if dpg.does_item_exist("show_steps_to_code_prufer"):
        dpg.set_item_label("show_steps_to_code_prufer", t["show_steps"])
    if dpg.does_item_exist("show_steps_to_graph_prufer"):
        dpg.set_item_label("show_steps_to_graph_prufer", t["show_steps"])
    if dpg.does_item_exist("choose_step_prufer"):
        dpg.set_value("choose_step_prufer", t["choose_step"])
    if dpg.does_item_exist("choose_step_to_prufer"):
        dpg.set_value("choose_step_to_prufer", t["choose_step"])
    if dpg.does_item_exist("tree_input_label"):
        dpg.set_value("tree_input_label", t["tree_input_label"])
    if dpg.does_item_exist("graph_input_label"):
        dpg.set_value("graph_input_label", t["graph_input_label"])
    if dpg.does_item_exist("show_prufer_code_button"):
        dpg.set_item_label("show_prufer_code_button", t["show_prufer_code_button"])
    if dpg.does_item_exist("edge_error_label"):
        dpg.set_value("edge_error_label", t["edge_error_label"])
    if dpg.does_item_exist("prufer_code_announcment_label"):
        dpg.set_value("prufer_code_announcment_label", t["prufer_code_announcment_label"])
    if dpg.does_item_exist("sheppard_code_announcment_label"):
        dpg.set_value("sheppard_code_announcment_label", t["sheppard_code_announcment_label"])
    dpg.set_value("prufer_code_hint", t["code_hint"])
    if dpg.does_item_exist("not_tree_error"):
        dpg.set_value("not_tree_error", t["not_tree_error"])
    if dpg.does_item_exist("bad_labeling_tree"):
        dpg.set_value("bad_labeling_tree", t["bad_labeling_tree"])

    # Sheppard
    dpg.set_value("sheppard_input_label", t["sheppard_input_label"])
    dpg.set_item_label("sheppard_button", t["sheppard_button"])
    dpg.set_value("sheppard_hint", t["sheppard_hint"])
    if dpg.does_item_exist("show_steps_to_code_sheppard"):
        dpg.set_item_label("show_steps_to_code_sheppard", t["show_steps"])
    if dpg.does_item_exist("show_steps_to_graph_sheppard"):
        dpg.set_item_label("show_steps_to_graph_sheppard", t["show_steps"])
    if dpg.does_item_exist("choose_step_sheppard"):
        dpg.set_value("choose_step_sheppard", t["choose_step"])
    if dpg.does_item_exist("show_sheppard_code_button"):
        dpg.set_item_label("show_sheppard_code_button", t["show_sheppard_code_button"])
    if dpg.does_item_exist("choose_step_to_sheppard"):
        dpg.set_value("choose_step_to_sheppard", t["choose_step"])
    if dpg.does_item_exist("graceful_error"):
        dpg.set_value("graceful_error", t["graceful_error"])
    if dpg.does_item_exist("from_graph_to_sheppard_error"):
        dpg.set_value("from_graph_to_sheppard_error", t["sheppard_error"])

    if dpg.does_item_exist("prufer_error"):
        dpg.set_value("prufer_error", t["prufer_error"])
    if dpg.does_item_exist("sheppard_error_text"):
        dpg.set_value("sheppard_error_text", t["sheppard_error"])
    if dpg.does_item_exist("to_code_sheppard_error_text"):
        dpg.set_value("to_code_sheppard_error_text", t["sheppard_error"])
    dpg.set_value("sheppard_code_hint", t["code_hint"])

def on_language_change(sender, app_data, user_data):
    if app_data == "Čeština":
        apply_language("cs")
    elif app_data == "Русский":
        apply_language("ru")
    else:
        apply_language("en")

# =========================================================
#                    KÓDY A OBRÁZKY
# =========================================================

def clear_step(code_type: str, DoNotDeleteMain: bool = False):
    for child in dpg.get_item_children(f"{code_type}_tab", 1):
        if dpg.get_item_type(child) == "mvAppItemType::mvImage":
            if dpg.get_item_label(child) == "main" and DoNotDeleteMain is True:
                continue
            dpg.delete_item(child)

def on_show_steps(sender, app_data, user_data):
    type = user_data["type"]
    destination = user_data["destination"]
    if user_data["destination"] == "to_code":
        edges = user_data["edges"]
    elif user_data["destination"] == "to_graph":
        code = user_data["code"]

    if dpg.does_item_exist(f"choose_step_{destination}_{type}"):
        dpg.delete_item(f"choose_step_{destination}_{type}")
    if dpg.does_item_exist(f"show_steps_{destination}_{type}"):
        dpg.delete_item(f"show_steps_{destination}_{type}")

    dpg.add_text(
        TRANSLATIONS[current_lang]["choose_step"],
        parent=f"{destination}_{type}",
        tag=f"choose_step_{destination}_{type}"
    )

    if destination == "to_code":
        max_step = (len(edges) - 1 if type == "prufer" else len(edges))
    elif destination == "to_graph":
        max_step = (len(code) + 1 if type == "prufer" else len(code))

    if destination == "to_code":
        graph = phi.Graph(phi.GraphType.UNDIRECTED)
        for edge in edges:
            graph.add_edge(edge[0], edge[1])

        if type == "prufer":
            graph.to_prufer(steps=True)
        else:
            graph.to_sheppard(steps=True)

    elif destination == "to_graph":
        if type == "prufer":
            phi.from_prufer(code, steps=True)
        else:
            phi.from_sheppard(code, steps=True)

    user_data = {"type": type, "destination": destination}
    dpg.add_slider_int(
        label="",
        min_value=1,
        max_value=max_step,
        default_value=1,
        tag=f"step_number_{destination}_{type}",
        parent=f"{destination}_{type}",
        callback=on_change_step,
        user_data=user_data,
    )
    on_change_step(None, None, user_data=user_data)

def on_change_step(sender, app_data, user_data):
    type = user_data["type"]
    destination = user_data["destination"]
    dpg.set_y_scroll("main_window", 10**9)

    step_number = dpg.get_value(f"step_number_{destination}_{type}")
    clear_step(type, DoNotDeleteMain=True)

    # ИЩЕМ step-картинки здесь:
    # outputs/prufer/graph_1_step.png и т.п.
    path = steps_dir(type) / f"{destination}_{step_number}_step.png"

    if not path.exists():
        print("not found")
        return

    width, height, channels, data = dpg.load_image(str(path))

    # один стабильный тег текстуры на вкладку (не плодим миллион)
    texture_tag = f"{destination}_{type}_step_texture"
    image_tag = f"{destination}_{type}_step_image"

    if dpg.does_item_exist(texture_tag):
        dpg.delete_item(texture_tag)
    if dpg.does_item_exist(image_tag):
        dpg.delete_item(image_tag)

    with dpg.texture_registry():
        dpg.add_static_texture(width, height, data, tag=texture_tag)

    dpg.add_image(texture_tag, parent=f"{destination}_{type}", tag=image_tag)

    dpg.set_y_scroll("main_window", 10**9)

def on_show_smth_button(sender, app_data, user_data):
    type = user_data["type"]
    destination = user_data["destination"]
    if destination == "to_code":
        text_edges = dpg.get_value(f"{type}_graph_input")
        try:
            edges = parse_edges(text_edges)
        except:
            return
    elif destination == "to_graph":
        text_code = dpg.get_value(f"{type}_input")
        try:
            code = parse_code(text_code)
        except ValueError:
            return
    
    if dpg.does_item_exist(f"{type}_code_label"):
        dpg.delete_item(f"{type}_code_label")
    if dpg.does_item_exist(f"step_number_{destination}_{type}"):
        dpg.delete_item(f"step_number_{destination}_{type}")
    if dpg.does_item_exist(f"{destination}_{type}_step_texture"):
        dpg.delete_item(f"{destination}_{type}_step_texture")
    if dpg.does_item_exist(f"{destination}_{type}_step_image"):
        dpg.delete_item(f"{destination}_{type}_step_image")
    if dpg.does_item_exist(f"show_steps_{destination}_{type}"):
        dpg.delete_item(f"show_steps_{destination}_{type}")
    if dpg.does_item_exist(f"{type}_code_announcment_label"):
        dpg.delete_item(f"{type}_code_announcment_label")
    if dpg.does_item_exist(f"choose_step_{destination}_{type}"):
        dpg.delete_item(f"choose_step_{destination}_{type}")
    if type == "sheppard":
        if dpg.does_item_exist(f"{destination}_sheppard_error_text"):
            dpg.delete_item(f"{destination}_sheppard_error_text")
        if dpg.does_item_exist("graceful_error"):
            dpg.delete_item("graceful_error")
    if type == "prufer":
        if dpg.does_item_exist("not_tree_error"):
            dpg.delete_item("not_tree_error")
        if dpg.does_item_exist("bad_labeling_tree"):
            dpg.delete_item("bad_labeling_tree")
        if dpg.does_item_exist("prufer_error"):
            dpg.delete_item("prufer_error")

    for tag in (f"{destination}_{type}_image", f"{destination}_{type}_texture"):
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)

    if destination == "to_code":
        graph = phi.Graph(phi.GraphType.UNDIRECTED)
        for edge in edges:
            graph.add_edge(edge[0], edge[1])

        graph_image = graph.export_to_png(f"{destination}_{type}_main.png", code_type=type, dark=True)
        width, height, channels, data = dpg.load_image(str(graph_image))

        with dpg.texture_registry():
            dpg.add_static_texture(width, height, data, tag=f"{destination}_{type}_texture")

        dpg.add_image(
            f"{destination}_{type}_texture",
            label="main",
            parent=f"{destination}_{type}",
            tag=f"{destination}_{type}_image"
        )

        if type == "prufer":
            if not graph.is_tree():
                dpg.add_text(TRANSLATIONS[current_lang]["not_tree_error"],
                            parent="to_code_prufer",
                            tag="not_tree_error")
                return
            if any(graph.node(id).id not in range(len(graph._nodes)) for id in graph.node_ids()):
                dpg.add_text(TRANSLATIONS[current_lang]["bad_labeling_tree"],
                             parent="to_code_prufer",
                             tag="bad_labeling_tree")
                return
            code_list = graph.to_prufer()

        else:
            code_list = graph.to_sheppard()
            if code_list is None:
                dpg.add_text(TRANSLATIONS[current_lang]["graceful_error"],
                            parent="to_code_sheppard",
                            tag="graceful_error")
                return
                
            if any(graph.node(id).id not in range(len(graph._edges) + 1) for id in graph.node_ids()):
                dpg.add_text(TRANSLATIONS[current_lang]["sheppard_error"],
                             parent="to_code_sheppard",
                             tag="to_code_sheppard_error_text")
                return
        
    else:
        if type == "sheppard":
            try:
                graph = phi.from_sheppard(code)
            except:
                dpg.add_text(TRANSLATIONS[current_lang]["sheppard_error"],
                             parent="to_graph_sheppard",
                             tag="to_graph_sheppard_error_text")
                return
            
        else:
            try:
                graph = phi.from_prufer(code)
            except:
                dpg.add_text(TRANSLATIONS[current_lang]["prufer_error"], 
                            parent="to_graph_prufer",
                            tag="prufer_error")
                return

    if destination == "to_graph":
        graph_image = graph.export_to_png(f"{destination}_{type}_main.png", code_type=type, dark=True)
        width, height, channels, data = dpg.load_image(str(graph_image))

        with dpg.texture_registry():
            dpg.add_static_texture(width, height, data, tag=f"{destination}_{type}_texture")

        dpg.add_image(
            f"{destination}_{type}_texture",
            label="main",
            parent=f"{destination}_{type}",
            tag=f"{destination}_{type}_image"
        )

    if destination == "to_code":
        dpg.add_text(TRANSLATIONS[current_lang][f"{type}_code_announcment_label"],
                     parent=f"to_code_{type}",
                     tag=f"{type}_code_announcment_label")
        dpg.add_text(str(code_list), 
                     parent=f"to_code_{type}",
                     tag=f"{type}_code_label")

    user_data = {"type": type, "destination": destination}
    if destination == "to_graph":
        user_data["code"] = code
    elif destination == "to_code":
        user_data["edges"] = edges

    dpg.add_button(
        tag=f"show_steps_{destination}_{type}",
        label=TRANSLATIONS[current_lang]["show_steps"],
        parent=f"{destination}_{type}",
        callback=on_show_steps,
        user_data=user_data,
    )

# =========================================================
#                        GUI
# =========================================================

with dpg.window(label="Graphium", tag="main_window", width=1000, height=700):
    with dpg.group(horizontal=True):
        dpg.add_text("", tag="lang_label_text")
        dpg.add_combo(
            items=["Čeština", "Русский", "English"],
            tag="lang_combo",
            default_value="Čeština",
            width=140,
            callback=on_language_change,
        )

    dpg.add_separator()

    with dpg.tab_bar():
        with dpg.tab(label="", tag="prufer_tab"):
            with dpg.tab_bar():
                with dpg.tab(label="From code to graph", tag="to_graph_prufer"):
                    dpg.add_text("", tag="prufer_input_label")
                    dpg.add_input_text(tag="prufer_input", width=300, default_value="")
                    dpg.add_button(label="", tag="prufer_button",
                                callback=on_show_smth_button, user_data={"type": "prufer", 
                                                                         "destination": "to_graph"})
                    dpg.add_separator()
                    dpg.add_text("", tag="prufer_hint")
                with dpg.tab(label="From graph to code", tag="to_code_prufer"):
                    dpg.add_text("", tag="tree_input_label")
                    dpg.add_input_text(tag="prufer_graph_input", width=300, default_value="")
                    dpg.add_button(label="", tag="show_prufer_code_button",
                                   callback=on_show_smth_button, user_data={"type": "prufer", 
                                                                            "destination": "to_code"})
                    dpg.add_separator()
                    dpg.add_text("", tag="prufer_code_hint")

        with dpg.tab(label="", tag="sheppard_tab"):
            with dpg.tab_bar():
                with dpg.tab(label="From code to graph", tag="to_graph_sheppard"):
                    dpg.add_text("", tag="sheppard_input_label")
                    dpg.add_input_text(tag="sheppard_input", width=300, default_value="")
                    dpg.add_button(label="", tag="sheppard_button",
                                callback=on_show_smth_button, user_data={"type": "sheppard", 
                                                                         "destination": "to_graph"})
                    dpg.add_separator()
                    dpg.add_text("", tag="sheppard_hint")
                with dpg.tab(label="From graph to code", tag="to_code_sheppard"):
                    dpg.add_text("", tag="graph_input_label")
                    dpg.add_input_text(tag="sheppard_graph_input", width=300, default_value="")
                    dpg.add_button(label="", tag="show_sheppard_code_button",
                                   callback=on_show_smth_button, user_data={"type": "sheppard", 
                                                                            "destination": "to_code"})
                    dpg.add_separator()
                    dpg.add_text("", tag="sheppard_code_hint")

# =========================================================
#                     SPUŠTĚNÍ APLIKACE
# =========================================================

def main():
    default_font = load_font()
    dpg.create_viewport(title="Graphium", width=1020, height=740)
    apply_language("cs")
    dpg.setup_dearpygui()
    dpg.show_viewport()

    if default_font is not None:
        dpg.bind_font(default_font)

    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()
