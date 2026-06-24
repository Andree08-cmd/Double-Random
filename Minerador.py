cat > /workspace/pipeline_escadinha_mpv2.py << 'EOF'
import chess
import chess.engine
import multiprocessing as mp
import threading
import time
import itertools
import os

# ==========================================
# CONFIGURAÇÕES DO MOTOR
# ==========================================
STOCKFISH_PATH = "/root/stockfish/stockfish/stockfish-ubuntu-x86-64-avx2"
OUTPUT_FILE = "/workspace/elite_final_mpv2.txt"

NUM_WORKERS = os.cpu_count() or 125 
HASH_SIZE = 512 
MAX_CP = 23 # Limite rigoroso do Ouro: +/- 0.23
CORTE_RASO_D12 = 80 # Nova Guilhotina: +/- 0.80

def generate_fens():
    pieces = ['R', 'R', 'N', 'N', 'B', 'B', 'Q', 'K']
    unique_perms = set(itertools.permutations(pieces))
    ranks = []
    
    for p in unique_perms:
        b_indices = [i for i, x in enumerate(p) if x == 'B']
        if (b_indices[0] % 2) == (b_indices[1] % 2): continue
        r_indices = [i for i, x in enumerate(p) if x == 'R']
        k_index = p.index('K')
        if not (r_indices[0] < k_index < r_indices[1]): continue
        ranks.append("".join(p))
    
    fens = []
    for black in ranks:
        b_lower = black.lower()
        b_castling = "".join([chr(ord('a') + i) for i, p in enumerate(b_lower) if p == 'r'])
        for white in ranks:
            w_castling = "".join([chr(ord('A') + i) for i, p in enumerate(white) if p == 'R'])
            fen = f"{b_lower}/pppppppp/8/8/8/8/PPPPPPPP/{white} w {w_castling}{b_castling} - 0 1"
            fens.append(fen)
    return fens

def worker(worker_id, fens_chunk, output_queue, progress_queue):
    try:
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        engine.configure({"Threads": 1, "Hash": HASH_SIZE})
        
        try:
            engine.configure({"UCI_Chess960": True})
        except:
            pass

        aprovadas_local = 0
        total_local = 0
        
        for fen in fens_chunk:
            try:
                board = chess.Board(fen, chess960=True)
                
                # ----------------------------------------------------
                # 1ª PARADA: O CORTE RASO AJUSTADO (Depth 12 | MPV=1)
                # ----------------------------------------------------
                info1 = engine.analyse(board, chess.engine.Limit(depth=12))
                if "score" not in info1: 
                    total_local += 1; progress_queue.put(1); continue
                    
                sc1 = info1["score"].white().score(mate_score=100000)
                if sc1 is None or abs(sc1) > CORTE_RASO_D12:
                    total_local += 1; progress_queue.put(1); continue
                
                # ----------------------------------------------------
                # 2ª PARADA: A MALHA FINA (Depth 23 | MPV=2)
                # ----------------------------------------------------
                info2 = engine.analyse(board, chess.engine.Limit(depth=23), multipv=2)
                if len(info2) < 2:
                    total_local += 1; progress_queue.put(1); continue
                    
                s1_2 = info2[0]["score"].white().score(mate_score=100000)
                s2_2 = info2[1]["score"].white().score(mate_score=100000)
                if s1_2 is None or s2_2 is None or abs(s1_2) > MAX_CP or abs(s2_2) > MAX_CP:
                    total_local += 1; progress_queue.put(1); continue
                
                # ----------------------------------------------------
                # 3ª PARADA: O SELO DE OURO (Depth 30 | MPV=2)
                # ----------------------------------------------------
                info3 = engine.analyse(board, chess.engine.Limit(depth=30), multipv=2)
                if len(info3) < 2:
                    total_local += 1; progress_queue.put(1); continue
                    
                s1_3 = info3[0]["score"].white().score(mate_score=100000)
                s2_3 = info3[1]["score"].white().score(mate_score=100000)
                
                if s1_3 is not None and s2_3 is not None:
                    if abs(s1_3) <= MAX_CP and abs(s2_3) <= MAX_CP:
                        output_queue.put(fen)
                        aprovadas_local += 1
                            
            except Exception as e:
                pass 
                
            total_local += 1
            progress_queue.put(1)
                    
        engine.quit()
        output_queue.put(None) 
        
    except Exception as e:
        output_queue.put(None)

def writer_thread(output_queue, real_workers):
    workers_finalizados = 0
    with open(OUTPUT_FILE, "a") as f:
        while True:
            item = output_queue.get()
            if item is None:
                workers_finalizados += 1
                if workers_finalizados == real_workers:
                    break
            else:
                f.write(item + "\n")
                f.flush()

def progress_thread(progress_queue, total_fens):
    analisadas = 0
    inicio = time.time()
    while analisadas < total_fens:
        progress_queue.get()
        analisadas += 1
        
        if analisadas % 500 == 0 or analisadas == total_fens:
            tempo = time.time() - inicio
            velocidade = analisadas / tempo if tempo > 0 else 0
            restante = total_fens - analisadas
            eta = restante / velocidade if velocidade > 0 else 0
            print(f"[MASTER] Progresso: {analisadas}/{total_fens} | Vel: {velocidade:.1f} FEN/s | ETA: {eta/3600:.1f}h", flush=True)

if __name__ == "__main__":
    print("\n[MASTER] Gerando 921.600 FENs de Double Random na memória RAM...")
    fens = generate_fens()
    total = len(fens)
    print(f"[MASTER] {total} FENs geradas. Detectados {NUM_WORKERS} núcleos.\n")
    
    chunk_size = (total // NUM_WORKERS) + 1
    chunks = [fens[i:i + chunk_size] for i in range(0, total, chunk_size)]
    REAL_WORKERS = len(chunks)
    
    output_queue = mp.Queue()
    progress_queue = mp.Queue()
    
    writer = threading.Thread(target=writer_thread, args=(output_queue, REAL_WORKERS), daemon=True)
    writer.start()
    
    progress = threading.Thread(target=progress_thread, args=(progress_queue, total), daemon=True)
    progress.start()
    
    processes = []
    print(f"[MASTER] Soltando os {REAL_WORKERS} cães de guerra na nuvem com a ESCADINHA D12 (0.80)->D23->D30!\n")
    for i, chunk in enumerate(chunks):
        p = mp.Process(target=worker, args=(i, chunk, output_queue, progress_queue))
        p.start()
        processes.append(p)
        
    for p in processes:
        p.join()
        
    writer.join()
    print("\n[MASTER] MISSÃO 100% CUMPRIDA! JOIAS SALVAS NO DISCO!\n")
EOF
