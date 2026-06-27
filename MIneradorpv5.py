cat > /workspace/pente_fino_2.py << 'EOF'
import chess
import chess.engine
import multiprocessing as mp
import threading
import time
import os

# ==========================================
# CONFIGURAÇÕES DO MOTOR E CAMINHOS
# ==========================================
STOCKFISH_PATH = "/root/stockfish/stockfish/stockfish-ubuntu-x86-64-avx2"

# Ajuste o nome do seu arquivo de entrada
INPUT_FILE = "/workspace/500_fens_brutas.txt" 
OUTPUT_FILE = "/workspace/500_fens_ouro.txt"

NUM_WORKERS = os.cpu_count() or 4  

# Configuração Beta - AGORA NO DEPTH 30
DEPTH_ALVO = 30
LIMIT_CP_PRINCIPAL = 23  # Linhas 1 e 2
LIMIT_CP_PERDAO = 70     # Linhas 3, 4 e 5 (Perdão Humano)

def worker(worker_id, fen_list, output_queue, progress_queue):
    try:
        engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
        engine.configure({
            "Threads": 1,
            "Hash": 256
        })
        
        try:
            engine.configure({"UCI_Chess960": True})
        except:
            pass
        
        for fen in fen_list:
            try:
                board = chess.Board(fen, chess960=True)
                
                # O Pente Fino de 5 Linhas (MultiPV = 5) no Depth 30
                info = engine.analyse(board, chess.engine.Limit(depth=DEPTH_ALVO), multipv=5)
                
                if len(info) < 5:
                    progress_queue.put(1)
                    continue
                
                aprovada = True
                for i, linha in enumerate(info):
                    score = linha["score"].white()
                    
                    if score.is_mate():
                        aprovada = False
                        break
                    
                    cp = score.score()
                    if cp is None:
                        aprovada = False
                        break
                        
                    # Regra de Ouro: Linhas 1 e 2 rigorosas, Linhas 3, 4 e 5 com perdão
                    limite = LIMIT_CP_PRINCIPAL if i < 2 else LIMIT_CP_PERDAO
                    if abs(cp) > limite:
                        aprovada = False
                        break
                
                if aprovada:
                    output_queue.put(fen)
                    
                progress_queue.put(1)
                
            except Exception as e:
                pass
                
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
        
        if analisadas % 10 == 0 or analisadas == total_fens:
            tempo = time.time() - inicio
            velocidade = analisadas / tempo if tempo > 0 else 0
            restante = total_fens - analisadas
            eta = restante / velocidade if velocidade > 0 else 0
            print(f"[BETA] {analisadas}/{total_fens} | {velocidade:.2f} FEN/s | ETA {eta:.1f} seg", flush=True)

if __name__ == "__main__":
    if not os.path.exists(INPUT_FILE):
        print(f"ARQUIVO NÃO ENCONTRADO: {INPUT_FILE}")
        exit()
        
    with open(INPUT_FILE, "r") as f:
        fens = [line.strip() for line in f if line.strip()]
    total_fens = len(fens)
    print(f"\n[SELENA] INICIANDO BETA COM {total_fens} FENS EM DEPTH 30\n")
    
    chunk_size = (total_fens // NUM_WORKERS) + 1
    chunks = [fens[i:i + chunk_size] for i in range(0, total_fens, chunk_size)]
    REAL_WORKERS = len(chunks)
    
    output_queue = mp.Queue()
    progress_queue = mp.Queue()
    
    writer = threading.Thread(target=writer_thread, args=(output_queue, REAL_WORKERS), daemon=True)
    writer.start()
    
    progress = threading.Thread(target=progress_thread, args=(progress_queue, total_fens), daemon=True)
    progress.start()
    
    processes = []
    for i, chunk in enumerate(chunks):
        p = mp.Process(target=worker, args=(i, chunk, output_queue, progress_queue))
        p.start()
        processes.append(p)
        
    for p in processes:
        p.join()
        
    writer.join()
    print("\n[SELENA] FENS OURO GERADAS COM SUCESSO!\n")
EOF
