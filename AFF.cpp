#include <iostream>
#include <vector>
#include <queue>
#include <limits>
#include <iomanip>
#include <string>
#include <algorithm>

using namespace std;

const double INF = numeric_limits<double>::infinity();

// =====================================================================
// --- CLASA PENTRU ALGORITMUL FORD-FULKERSON (Flux Maxim) ---
// =====================================================================
class FordFulkerson {
private:
    int n; 
    int source; 
    int sink; 
    vector<vector<double>> C; // Matricea de capacitati maxime
    vector<vector<double>> F; // Matricea de flux curent

    // Cautare in latime (BFS) pentru a gasi un drum nesaturat
    bool bfs(vector<int>& parent, bool forward_only) {
        fill(parent.begin(), parent.end(), -1);
        vector<bool> visited(n, false);
        queue<int> q;

        q.push(source);
        visited[source] = true;

        while (!q.empty()) {
            int u = q.front();
            q.pop();

            for (int v = 0; v < n; ++v) {
                if (!visited[v]) {
                    // In I_0, folosim doar arcele care exista fizic in sens direct
                    if (forward_only && C[u][v] == 0) {
                        continue; 
                    }

                    // Capacitatea reziduala (cat mai putem pompa)
                    double capacitate_reziduala = C[u][v] - F[u][v];

                    if (capacitate_reziduala > 0) {
                        q.push(v);
                        parent[v] = u;
                        visited[v] = true;
                        
                        if (v == sink) {
                            return true; // Am gasit un drum pana la destinatie
                        }
                    }
                }
            }
        }
        return false;
    }

    // Functie ajutatoare pentru a afisa starea retelei
    void afiseazaStareRetea() {
        cout << "   [Starea curenta a arcelor folosite]\n";
        for (int i = 0; i < n; ++i) {
            for (int j = 0; j < n; ++j) {
                if (C[i][j] > 0 && F[i][j] > 0) {
                    cout << "    - Arc (x" << i + 1 << " -> x" << j + 1 << "): Flux " 
                         << F[i][j] << " / Cap " << C[i][j] << "\n";
                }
            }
        }
        cout << "\n";
    }

public:
    void solve(int noduri, int s, int t, vector<vector<double>> capacitati) {
        n = noduri;
        source = s;
        sink = t;
        C = capacitati;
        F.assign(n, vector<double>(n, 0.0));

        vector<int> parent(n);
        double max_flow = 0;

        cout << "\n=======================================================================\n";
        cout << "--- INCEPERE EXECUTIE: ALGORITMUL FORD-FULKERSON ---\n";
        cout << "=======================================================================\n";

        // -------------------------------------------------------------------
        // PASUL 1: ITERATIA I_0 (Determinarea fluxului initial f0)
        // -------------------------------------------------------------------
        cout << "\n>>> ETAPA I_0: Cautarea drumurilor saturate (fara reorientari) <<<\n\n";
        bool gasit_in_i0 = false;
        int step = 1;
        
        while (bfs(parent, true)) {
            gasit_in_i0 = true;
            double path_flow = INF;

            // Colectam drumul pentru afisare frumoasa
            vector<int> path;
            for (int v = sink; v != source; v = parent[v]) {
                path.push_back(v);
            }
            path.push_back(source);
            reverse(path.begin(), path.end());

            cout << "Pasul " << step++ << ":\n";
            cout << " -> S-a gasit drumul: ";
            for (size_t i = 0; i < path.size(); ++i) {
                cout << "x" << path[i] + 1;
                if (i < path.size() - 1) cout << " -> ";
            }
            cout << "\n";

            // Calculam valoarea fluxului ce poate fi pompat (bottleneck)
            cout << " -> Calcul capacitate drum (minimul capacitatilor reziduale):\n    min(";
            for (int v = sink; v != source; v = parent[v]) {
                int u = parent[v];
                double cap_rez = C[u][v] - F[u][v];
                path_flow = min(path_flow, cap_rez);
                cout << cap_rez;
                if (u != source) cout << ", ";
            }
            cout << ") = " << path_flow << "\n";

            // Actualizam matricea de flux
            for (int v = sink; v != source; v = parent[v]) {
                int u = parent[v];
                F[u][v] += path_flow;
                F[v][u] -= path_flow; // Adaugam flux negativ pe drumul invers (graful rezidual)
            }

            max_flow += path_flow;
            cout << " -> Flux adaugat pe acest drum: " << path_flow << "\n";
            afiseazaStareRetea();
        }

        if (!gasit_in_i0) {
            cout << " -> Nu s-au gasit drumuri in Etapa I_0.\n";
        } else {
            cout << "=> Flux initial total acumulat (f0): " << max_flow << "\n";
        }

        // -------------------------------------------------------------------
        // PASUL 2: ITERATIILE I_k (Procedura de marcaj pe graful rezidual)
        // -------------------------------------------------------------------
        cout << "\n=======================================================================\n";
        cout << ">>> ETAPA I_k: Cautarea cu marcaj (Permite reorientarea fluxului) <<<\n\n";
        int iteratie = 1;
        
        while (bfs(parent, false)) {
            double path_flow = INF;

            vector<int> path;
            for (int v = sink; v != source; v = parent[v]) {
                path.push_back(v);
            }
            path.push_back(source);
            reverse(path.begin(), path.end());

            cout << "Iteratia I_" << iteratie++ << ":\n";
            cout << " -> Lant gasit (posibila reorientare): ";
            for (size_t i = 0; i < path.size(); ++i) {
                cout << "x" << path[i] + 1;
                if (i < path.size() - 1) cout << " -> ";
            }
            cout << "\n";

            // Calculam minimul pe lantul rezidual
            cout << " -> Calcul capacitate reorientare:\n    min(";
            for (int v = sink; v != source; v = parent[v]) {
                int u = parent[v];
                double cap_rez = C[u][v] - F[u][v];
                path_flow = min(path_flow, cap_rez);
                cout << cap_rez;
                if (u != source) cout << ", ";
            }
            cout << ") = " << path_flow << "\n";

            // Actualizam
            for (int v = sink; v != source; v = parent[v]) {
                int u = parent[v];
                F[u][v] += path_flow;
                F[v][u] -= path_flow; 
            }

            max_flow += path_flow;
            cout << " -> Flux suplimentar obtinut: " << path_flow << "\n";
            afiseazaStareRetea();
        }

        cout << "\n>>> STOP ALGORITM: Destinatia nu mai poate fi atinsa (S-a atins taietura minima)! <<<\n";
        cout << "=======================================================================\n\n";
        
        cout << "###########################################\n";
        cout << "# FLUXUL MAXIM TOTAL IN RETEA: " << setw(10) << max_flow << " #\n";
        cout << "###########################################\n";
    }
};

// =====================================================================
// --- FUNCTIA PRINCIPALA ---
// =====================================================================
int main() {
    int n, sursa, dest;
    
    cout << "======================================================\n";
    cout << "   OPTIMIZARE FLUX DE DATE (HACKATHON NETWORK)        \n";
    cout << "======================================================\n";
    
    cout << "Numar total de noduri (inclusiv sursa si destinatie): ";
    if (!(cin >> n)) return 0;
    
    cout << "Nodul sursa (ex: 1 pentru Server): ";
    cin >> sursa;
    
    cout << "Nodul destinatie (ex: " << n << " pentru Sala de Hackathon): ";
    cin >> dest;

    vector<vector<double>> C(n, vector<double>(n, 0.0));
    cout << "\nIntroduceti capacitatile cablurilor/conexiunilor in Mbps.\n";
    cout << "(Daca nu exista cablu direct intre noduri, introduceti 0)\n\n";
    
    for (int i = 0; i < n; ++i) {
        for (int j = 0; j < n; ++j) {
            if (i != j) {
                cout << "Capacitate arc (x" << i + 1 << " -> x" << j + 1 << "): ";
                cin >> C[i][j];
            }
        }
    }

    FordFulkerson aff;
    aff.solve(n, sursa - 1, dest - 1, C);

    cout << "\nProgram incheiat. Apasa Enter pentru a iesi...";
    cin.ignore();
    cin.get();
    return 0;
}