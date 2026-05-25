import streamlit as st
import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

# ==========================================
# ALGORITMUL FORD-FULKERSON (LOGICĂ STRUCTURATĂ)
# ==========================================
def run_ford_fulkerson(n, source, sink, C):
    
    # ==========================================
    # PASUL 1: Inițializarea fluxului
    # ==========================================
    F = np.zeros((n, n))
    states = [] 
    
    #BFS
    def bfs(forward_only):
        parent = [-1] * n
        visited = [False] * n
        queue = [source]
        visited[source] = True
        
        while queue:
            u = queue.pop(0)
            for v in range(n):
                if not visited[v]:
                    if forward_only and C[u][v] == 0:
                        continue
                    
                    cap_rez = C[u][v] - F[u][v]
                    if cap_rez > 0:
                        queue.append(v)
                        parent[v] = u
                        visited[v] = True
                        if v == sink:
                            return True, parent, visited
        return False, parent, visited

    states.append({
        'F': F.copy(),
        'path': [],
        'phase': "Inițial",
        'log_text': "### PASUL 1: Inițializarea fluxului\nStarea inițială a rețelei. Niciun flux nu a fost trimis încă.\n\n**Test Optimalitate:** Începem evaluarea."
    })

    max_flow = 0
    step = 1
    final_visited = [] # Aici vom salva starea vizitelor cand se opreste algoritmul
    
    # -------------------------------------------------------------------
    # ETAPA I_0 (Drumuri directe)
    # -------------------------------------------------------------------
    while True:
        # PASUL 2: Testarea optimalității (Marcare)
        found, parent, visited = bfs(forward_only=True)
        if not found:
            break
            
        # PASUL 3: Îmbunătățirea fluxului
        path = []
        curr = sink
        while curr != source:
            path.append(curr)
            curr = parent[curr]
        path.append(source)
        path.reverse()
        
        bottlenecks = []
        path_flow = float('Inf')
        for i in range(len(path)-1):
            u, v = path[i], path[i+1]
            cap_rez = C[u][v] - F[u][v]
            bottlenecks.append(str(int(cap_rez)))
            path_flow = min(path_flow, cap_rez)
            
        log_text = f"#### ETAPA I_0 - Pasul {step}\n"
        log_text += f"**-> PASUL 2 (Test Optimalitate):** Destinația a putut fi marcată. Fluxul curent **NU este optim**, continuăm.\n\n"
        log_text += f"**-> Traseu găsit:** " + " -> ".join([f"x{x+1}" for x in path]) + "\n"
        log_text += f"**-> PASUL 3 (Îmbunătățire):** Calcul gâtuire:\n"
        log_text += f"min(" + ", ".join(bottlenecks) + f") = **{int(path_flow)}**\n\n"
        
        for i in range(len(path)-1):
            u, v = path[i], path[i+1]
            F[u][v] += path_flow
            F[v][u] -= path_flow
            
        max_flow += path_flow
        
        log_text += f"Flux adăugat: {int(path_flow)}\n\n"
        log_text += f"--- \n*[Starea curentă a arcelor folosite]*\n"
        for i in range(n):
            for j in range(n):
                if C[i][j] > 0 and F[i][j] > 0:
                    log_text += f"\n- Arc (x{i+1} -> x{j+1}): Flux **{int(F[i][j])}** / Cap {int(C[i][j])}"
                    
        states.append({
            'F': F.copy(),
            'path': path,
            'phase': f"Etapa I_0 (Pas {step})",
            'log_text': log_text
        })
        step += 1

    # -------------------------------------------------------------------
    # ETAPA I_k (Reorientari în graful rezidual)
    # -------------------------------------------------------------------
    step_k = 1
    while True:
        # PASUL 2: Testarea optimalității (Marcare)
        found, parent, visited = bfs(forward_only=False)
        if not found:
            final_visited = visited # Salvăm cine a putut fi vizitat la ultimul pas
            break
            
        # PASUL 3: Îmbunătățirea fluxului
        path = []
        curr = sink
        while curr != source:
            path.append(curr)
            curr = parent[curr]
        path.append(source)
        path.reverse()
        
        bottlenecks = []
        path_flow = float('Inf')
        for i in range(len(path)-1):
            u, v = path[i], path[i+1]
            cap_rez = C[u][v] - F[u][v]
            bottlenecks.append(str(int(cap_rez)))
            path_flow = min(path_flow, cap_rez)
            
        log_text = f"#### ETAPA I_k - Iterația {step_k} (Reorientare)\n"
        log_text += f"**-> PASUL 2 (Test Optimalitate):** Destinația a putut fi marcată în graful rezidual. Fluxul curent **NU este optim**, continuăm.\n\n"
        log_text += f"**-> Lanț găsit:** " + " -> ".join([f"x{x+1}" for x in path]) + "\n"
        log_text += f"**-> PASUL 3 (Îmbunătățire):** Calcul reorientare:\n"
        log_text += f"min(" + ", ".join(bottlenecks) + f") = **{int(path_flow)}**\n\n"
        
        for i in range(len(path)-1):
            u, v = path[i], path[i+1]
            F[u][v] += path_flow
            F[v][u] -= path_flow
            
        max_flow += path_flow
        
        log_text += f"Flux suplimentar adăugat: {int(path_flow)}\n\n"
        log_text += f"--- \n*[Starea curentă a arcelor folosite]*\n"
        for i in range(n):
            for j in range(n):
                if C[i][j] > 0 and F[i][j] > 0:
                    log_text += f"\n- Arc (x{i+1} -> x{j+1}): Flux **{int(F[i][j])}** / Cap {int(C[i][j])}"
                    
        states.append({
            'F': F.copy(),
            'path': path,
            'phase': f"Etapa I_k (Iterația {step_k})",
            'log_text': log_text
        })
        step_k += 1

    # ==========================================
    # PASUL 4: Afișarea soluției și a mulțimii T
    # ==========================================
    # Calculăm mulțimile S (vizitat) și T (nevizitat)
    S_nodes = [f"x{i+1}" for i in range(n) if final_visited[i]]
    T_nodes = [f"x{i+1}" for i in range(n) if not final_visited[i]]
    
    str_S = "{" + ", ".join(S_nodes) + "}"
    str_T = "{" + ", ".join(T_nodes) + "}"

    mesaj_final = f"### PASUL 4: Afișarea soluției\n"
    mesaj_final += f"**-> PASUL 2 (Test Optimalitate):** BFS a fost blocat de arcele saturate. Destinația **NU a mai putut fi marcată**. Fluxul este **OPTIM**!\n\n"
    mesaj_final += f"---\n"
    mesaj_final += f"**Identificarea Tăieturii Minime (S, T):**\n"
    mesaj_final += f"- **S** (Noduri marcate/accesibile) = {str_S}\n"
    mesaj_final += f"- **T** (Noduri nemarcate/inaccesibile) = **{str_T}**\n\n"
    mesaj_final += f"*(Muchiile roșii din grafic separă mulțimea S de mulțimea T)*\n\n"
    mesaj_final += f"---\n## FLUXUL MAXIM TOTAL: {int(max_flow)}"
    
    states.append({
        'F': F.copy(),
        'path': [],
        'phase': "Algoritm Finalizat",
        'log_text': mesaj_final
    })
    
    return states, max_flow

# ==========================================
# INTERFATA STREAMLIT
# ==========================================
st.set_page_config(page_title="Optimizare Flux - Ford-Fulkerson", layout="wide")
st.title("Algoritmul Ford-Fulkerson (Teoria Grafurilor)")

# Sidebar
st.sidebar.header("Setări Rețea")
n_nodes = st.sidebar.number_input("Număr total noduri", min_value=2, max_value=20, value=10)
source = st.sidebar.number_input("Nod Sursă", min_value=1, max_value=n_nodes, value=1) - 1
sink = st.sidebar.number_input("Nod Destinație", min_value=1, max_value=n_nodes, value=10) - 1

st.sidebar.subheader("Introdu Capacitățile Manual")
st.sidebar.info("💡 **Ghid:** \n- Dublu-click pe o celulă pentru a o edita.\n- Click pe rândul gol de jos pentru a adăuga muchii.\n- Selectează un rând și apasă 'Delete' pentru a-l șterge.")

# Tabel curat, cu un singur rand demonstrativ
default_edges = pd.DataFrame([
    {"De la": 1, "La": 2, "Capacitate": 10}
])
edited_df = st.sidebar.data_editor(default_edges, num_rows="dynamic", height=500)

if st.sidebar.button("Rulează Algoritmul", type="primary"):
    C = np.zeros((n_nodes, n_nodes))
    for _, row in edited_df.iterrows():
        try:
            u, v, cap = int(row["De la"])-1, int(row["La"])-1, float(row["Capacitate"])
            if 0 <= u < n_nodes and 0 <= v < n_nodes:
                C[u][v] = cap
        except:
            pass
            
    states, max_flow = run_ford_fulkerson(n_nodes, source, sink, C)
    st.session_state['states'] = states
    st.session_state['C'] = C
    st.session_state['n_nodes'] = n_nodes

# Afisarea starii
if 'states' in st.session_state:
    states = st.session_state['states']
    C = st.session_state['C']
    n_nodes = st.session_state['n_nodes']
    
    st.markdown("---")
    step_idx = st.slider("Navighează prin pașii algoritmului:", 0, len(states)-1, 0)
    
    current_state = states[step_idx]
    F = current_state['F']
    path = current_state['path']
    
    col_text, col_graf = st.columns([1.2, 2.8])
    
    with col_text:
        st.info(f"**Status Curent:** {current_state['phase']}")
        st.markdown(current_state['log_text'])
            
    with col_graf:
        fig, ax = plt.subplots(figsize=(12, 7)) 
        G = nx.DiGraph()
        
        for i in range(n_nodes):
            G.add_node(i)
        for i in range(n_nodes):
            for j in range(n_nodes):
                if C[i][j] > 0:
                    G.add_edge(i, j)
                    
        # Coordonate pentru 10 noduri (design conform caietului)
        if n_nodes == 10:
            pos = {
                0: (0, 0),     # x1 (Sursa)
                1: (2, 3),     # x2
                2: (2, 0),     # x3
                3: (2, -3),    # x4
                4: (4, 1.5),   # x5
                5: (4, -1.5),  # x6
                6: (6, 3),     # x7
                7: (6, 0),     # x8
                8: (6, -3),    # x9
                9: (8, 0)      # x10 (Destinatia)
            }
        else:
            pos = nx.shell_layout(G)
            
        edge_colors = []
        edge_widths = []
        path_edges = [(path[i], path[i+1]) for i in range(len(path)-1)] if path else []
        
        for u, v in G.edges():
            # Dacă suntem la pasul final, colorăm arcele saturate
            if current_state['phase'] == "Algoritm Finalizat" and C[u][v] > 0 and abs(C[u][v] - F[u][v]) < 1e-5:
                edge_colors.append('#FF4B4B')  
                edge_widths.append(3.5)        
            # În timpul pașilor intermediari, colorăm drumul curent de pompare
            elif (u, v) in path_edges or (v, u) in path_edges:
                edge_colors.append('#FF4B4B')  
                edge_widths.append(3.0)        
            else:
                edge_colors.append('gray')     
                edge_widths.append(1.0)
                
        edge_labels = {}
        for u, v in G.edges():
            edge_labels[(u, v)] = f"{int(F[u][v])} / {int(C[u][v])}"

        nx.draw_networkx_edges(G, pos, ax=ax, edge_color=edge_colors, width=edge_widths, 
                               arrows=True, arrowsize=20)
        
        nx.draw_networkx_nodes(G, pos, ax=ax, node_color='#A0C4FF', node_size=1200, 
                               edgecolors='dimgray', linewidths=1.5)
        
        nx.draw_networkx_labels(G, pos, ax=ax, labels={i: f"x{i+1}" for i in G.nodes()}, 
                                font_weight='bold', font_size=11)
                
        nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, ax=ax, 
                                     font_color='black', font_size=9, label_pos=0.35,
                                     bbox=dict(facecolor='white', edgecolor='none', alpha=0.85, pad=1))
        
        ax.axis('off')
        fig.tight_layout()
        st.pyplot(fig)