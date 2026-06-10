from Diktyonphi import Graph, GraphType
import Diktyonphi as phi
import glob, time, os
from itertools import islice
from pathlib import Path
from paths import data_dir
from concurrent.futures import ProcessPoolExecutor, as_completed
import shutil

def print_status(msg: str) -> None:
    width = shutil.get_terminal_size((100, 20)).columns - 1
    msg = msg[:width]
    print("\r" + msg.ljust(width), end="", flush=True)

def find_center(tree: Graph):
    copy_tree = tree.copy()
    if len(copy_tree._nodes) in [0, 1, 2]:
        return list(copy_tree.node_ids())
    leaves = [copy_tree.node(id).id for id in copy_tree.node_ids() if copy_tree.node(id).out_degree==1]

    def delete_leaves(leaves):
        new_leaves = []
        for leaf in leaves:
            neighbor_id = next(copy_tree.node(leaf).neighbor_ids)
            copy_tree.del_node(leaf)
            if copy_tree.node(neighbor_id).out_degree == 1:
                new_leaves.append(neighbor_id)

        if len(copy_tree._nodes) in [0, 1, 2]:
            return list(copy_tree.node_ids())
        
        return delete_leaves(new_leaves)

    return delete_leaves(leaves)

def is_isomorphic_degree_signature(tree1: Graph, PATTERN_DEGREE):
    if tree1.degree_signature() != PATTERN_DEGREE:
        return False
    return True

def is_isomorphic_binary_code(tree1: Graph, PATTERN_BINARY):
    if tree1.min_binary_code() != PATTERN_BINARY:
        return False
    return True

def check_batch_sheppard(codes_batch, n, mode, involution=None, PATTERN_DEGREE=None, PATTERN_BINARY=None):
    """
    Zpracuje dávku Sheppardových kódů a vrátí odpovídající
    Prüferovy kódy stromů, které splňují zadané podmínky.
    
    Parametry:
        codes_batch (list): seznam Sheppardových kódů délky n-1.
        n (int): počet vrcholů.
        mode (str): které ohodnocení se počítá (obecné graceful, ordered graceful či alpha).
        involution (bool): zda se má přidat i involutorní kód.
        PATTERN_DEGREE (tuple | None): multimnožina stupňů vzorového stromu.
        PATTERN_BINARY (str | None): binární kód vzorového stromu.
    
    Návratová hodnota:
        list[tuple[int, ...]]: seznam Prüferových kódů.
    """
    results = []

    for shep in codes_batch:
        if mode == "alpha":
            if not phi.is_sheppard_code_alpha(shep):
                continue

        if not phi.sheppard_uses_all_vertices(shep, n):
            continue

        tree = phi.from_sheppard(shep)
        if len(tree.DFS()) != n:
            continue

        if PATTERN_DEGREE is not None and PATTERN_BINARY is not None:
            if is_isomorphic_degree_signature(tree, PATTERN_DEGREE) == False:
                continue

            if is_isomorphic_binary_code(tree, PATTERN_BINARY) == False:
                continue

        if mode == "ordered":
            if not tree.is_labeling_ordered():
                continue
            
        pr = tuple(tree.to_prufer())
        results.append(pr)

        if involution:
            inv_pr = tuple(tree.involute().to_prufer())
            results.append(inv_pr)

    return results

def sort_and_index_file(filepath: str, n: int, sort: bool = False, rank: bool = False) -> None:
    """
    Čte soubor, kde každý řádek představuje jeden Prüferův kód jako čísla oddělená mezerou:
        „x1 x2 ... x_{n-2}“

    Volitelně:
    - seřadí kódy podle lexikografického pořadí v prostoru Prüferových kódů,
    - doplní ke každému kódu jeho lexikografický index.

    Výstupní formát:
    - bez indexace:      „x1 x2 ... x_{n-2}“
    - s indexací:        „<index>  x1 x2 ... x_{n-2}“
    """
    if not os.path.isfile(filepath):
        print(f"[index] Soubor nenalezen: {filepath}")
        return

    k = n - 2
    codes: list[tuple[int, ...]] = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            s = line.strip()
            if not s:
                continue

            parts = s.split()
            try:
                nums = [int(p) for p in parts]
            except ValueError:
                continue

            if len(nums) == k:
                code = tuple(nums)
            elif len(nums) == k + 1:
                code = tuple(nums[1:])
            else:
                continue

            if any(not (0 <= x <= n - 1) for x in code):
                continue

            codes.append(code)

    if not codes:
        print(f"[index] Žádné platné kódy v souboru: {filepath}")
        return

    if sort:
        codes.sort(key=lambda c: phi.prufer_lex_rank(c, n))

    w = 0
    if rank:
        max_rank = max(phi.prufer_lex_rank(code, n) for code in codes)
        w = len(str(max_rank))

    with open(filepath, "w", encoding="utf-8") as f:
        for code in codes:
            if rank:
                r = phi.prufer_lex_rank(code, n)
                f.write(f"{r:>{w}}  " + " ".join(map(str, code)) + "\n")
            else:
                f.write(" ".join(map(str, code)) + "\n")

    print(
        f"[index] Hotovo: "
        f"sort={sort}, rank={rank}, přepsán soubor: {filepath}"
    )

def take_batch(it, batch_size):
    """Vezme z iterátoru další dávku o velikosti batch_size (nebo méně)."""
    return list(islice(it, batch_size))

def graceful_prufer_codes_n(
    n=10,
    mode: str | None = "graceful",
    pattern: Graph | None = None,
    output_dir: Path | None = None,
    output_file: str | None = None,
    workers: int | None = 2,
    batch_size: int | None = 12000,
    max_inflight: int | None = 12,
    heartbeat_sec: int | None = 4,
    buf_write_every: int | None = 30_000,
    index: bool | None = False,
    sort: bool | None = False,
    involution: bool | None = True,
    max_file_mb: int | None = 50,
):
    """
    Hlavní paralelní procedura pro generování graciózních 
    Prüferových kódů pro daný počet vrcholů n.

    Vstup:
        n (int): počet vrcholů stromů.
        mode (str): typ graciózního ohodnocení.
        pattern (Graph | None): volitelný vzorový strom pro filtraci.
        output_dir (Path | None): cílový adresář pro výstupní soubory.
        output_file (str | None): základní název výstupních souborů.
        workers (int): počet paralelních procesů.
        batch_size (int): velikost dávky Sheppardových kódů.
        max_inflight (int): maximální počet paralelně zpracovávaných dávek.
        heartbeat_sec (int): interval výpisu průběžných statistik.
        buf_write_every (int): velikost interního bufferu pro zápis.
        rank (bool): zda musí být ke kódu přepsáno jeho pořadové číslo
        sort (bool): zda mají být výstupní soubory lexikograficky seřazeny.
        involution (bool): zda se mají generovat i involutorní kódy.
        max_file_mb (int): maximální velikost jednoho výstupního souboru.

    Výstup:
        Funkce vrací None.
        Výsledkem jsou textové soubory obsahující všechny nalezené
        graciózní Prüferovy kódy v daném rozsahu.
    """

    print(mode)
    if output_dir is not None:
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
    else:
        out_dir = data_dir() / f"n={n}"
        out_dir.mkdir(parents=True, exist_ok=True)

    if output_file is None:
        base_name = f"graceful_prufer_{n}_sort" if sort else f"graceful_prufer_{n}"
    else:
        base_name = Path(os.path.abspath(output_file)).stem

    limit_bytes = int(max_file_mb) * 1024 * 1024

    def make_part_path(part_idx: int) -> Path:
        """Cesta k souboru."""
        return out_dir / f"{base_name}_part_{part_idx:03d}.txt"

    total_sheppard = 0
    total_prufer = 0

    t0 = time.perf_counter()
    last_print = t0
    last_total_sheppard = 0

    print(
        f"[main] n={n}, workers={workers}, batch_size={batch_size}, "
        f"max_inflight={max_inflight}, max_file_mb={max_file_mb}",
        flush=True,
    )

    codes_iter = phi.all_sheppard_codes(n)
    buf = []

    with ProcessPoolExecutor(max_workers=workers) as ex:
        part_idx = 1
        out_path = make_part_path(part_idx)
        out = open(out_path, "w", encoding="utf-8")
        current_size = 0

        if pattern:
            PATTERN_DEGREE = pattern.degree_signature()
            PATTERN_BINARY = pattern.min_binary_code()
        else:
            PATTERN_DEGREE, PATTERN_BINARY = None, None

        def flush_buf():
            """
            Zapsat buffer do souboru.
            Formát: čísla oddělená mezerou, jeden řádek = jeden Prüferův kód.
            """
            nonlocal out, current_size, part_idx, out_path, buf
            if not buf:
                return

            lines = [" ".join(str(x) for x in pr) for pr in buf]
            text = "\n".join(lines) + "\n"

            data = text.encode("utf-8")
            size = len(data)

            if current_size + size > limit_bytes and current_size > 0:
                out.close()
                part_idx += 1
                out_path = make_part_path(part_idx)
                out = open(out_path, "w", encoding="utf-8")
                current_size = 0

            out.write(text)
            current_size += size
            buf.clear()

        try:
            inflight = set()
            fut_sizes = {}

            while len(inflight) < max_inflight:
                batch = take_batch(codes_iter, batch_size)
                if not batch:
                    break
                fut = ex.submit(check_batch_sheppard, batch, n, mode, involution, PATTERN_DEGREE, PATTERN_BINARY)
                inflight.add(fut)
                fut_sizes[fut] = len(batch)

            while inflight:
                done_any = False

                for fut in as_completed(list(inflight)):
                    inflight.remove(fut)
                    batch_size_done = fut_sizes.pop(fut, 0)

                    total_sheppard += batch_size_done

                    prufer_list = fut.result()
                    total_prufer += len(prufer_list)

                    for pr in prufer_list:
                        buf.append(pr)
                        if len(buf) >= buf_write_every:
                            flush_buf()

                    batch = take_batch(codes_iter, batch_size)
                    if batch:
                        new_fut = ex.submit(check_batch_sheppard, batch, n, mode, involution, PATTERN_DEGREE, PATTERN_BINARY)
                        inflight.add(new_fut)
                        fut_sizes[new_fut] = len(batch)

                    done_any = True
                    
                now = time.perf_counter()
                if (not done_any) or (now - last_print >= heartbeat_sec):
                    elapsed = now - t0
                    elapsed_str = time.strftime("%H:%M:%S", time.gmtime(elapsed))
                    avg = total_sheppard / elapsed if elapsed > 0 else 0.0
                    inst = (
                        (total_sheppard - last_total_sheppard) / (now - last_print)
                        if now > last_print else 0.0
                    )
                    msg = (
                        f"[hb] Š={total_sheppard:,} | "
                        f"P={total_prufer:,} | "
                        f"avg={avg:,.0f}/s | "
                        f"cur={inst:,.0f}/s | "
                        f"t={elapsed_str}"
                    )

                    print_status(msg)
                    last_print = now
                    last_total_sheppard = total_sheppard

            flush_buf()

        finally:
            out.close()

    elapsed = time.perf_counter() - t0
    print()

    written = (
        f"zapsaných Prüfer-kódů (včetně involucí): {total_prufer:,} | "
        if involution else
        f"zapsaných Prüfer-kódů (bez involucí): {total_prufer:,} | "
    )

    print(
        f"[done] Zkontrolováno Shepppard-kódů: {total_sheppard:,} | "
        f"{written}"
        f"průměrně ~{total_sheppard/elapsed:,.0f}/s | "
        f"výstup v adresáři: {out_dir} | soubory: {base_name}_part_XXX.txt",
        flush=True,
    )

    if sort or index:
        pattern_glob = str(out_dir / f"{base_name}_part_*.txt")
        part_files = sorted(glob.glob(pattern_glob))

        print(
            f"[post] sort={sort}, index={index}, zpracovávám jednotlivé části "
            f"({len(part_files)} souborů)...",
            flush=True,
        )

        for path in part_files:
            print(f"[post] -> {os.path.basename(path)}", flush=True)
            sort_and_index_file(path, n, sort, index)

if __name__ == "__main__":
    n=11
    graceful_prufer_codes_n(n=n,
                            workers=6,
                            involution=True,
                            batch_size=80000, 
                            buf_write_every=100,
                            max_inflight=40,
                            heartbeat_sec=5,
                            sort = True,
                            rank = True,
                            output_dir=fr"C:\Users\Igor\Desktop\Python-programs\bachelors\Graphium\data\n={n}",
                            output_file=f"graceful_trees_{n}.txt"
    )
