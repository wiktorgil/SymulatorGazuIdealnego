# 🧪 Symulacja Mieszanin Gazów Idealnych

Interaktywna symulacja 2D mieszaniny trzech gazów idealnych oparta na fizyce kinetycznej.
Napisana w Pythonie z użyciem biblioteki Pygame.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Pygame](https://img.shields.io/badge/Pygame-2.x-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 📸 Zrzut ekranu

<img width="999" height="696" alt="11" src="https://github.com/user-attachments/assets/69c5bbff-e7b8-482b-8d0a-ddfaa1816371" />

---

## 📌 Opis projektu

Program symuluje zachowanie mieszaniny trzech różnych gazów idealnych zamkniętych
w prostokątnym naczyniu. Każdy gaz reprezentowany jest przez
cząstki o różnej masie i promieniu poruszające się zgodnie z prawami mechaniki klasycznej.

Symulacja pozwala obserwować w czasie rzeczywistym:
- **Rozkład prędkości Maxwell-Boltzmann** — histogram dla każdego gazu osobno
- **Eqipartycję energii kinetycznej** — gazy o różnej masie mają tę samą ⟨Ek⟩
- **Dynamiczne ciśnienie** — obliczane z przekazu pędu cząstek do ścian naczynia
- **Zderzenia sprężyste** — między cząstkami i ze ścianami

---

## ⚙️ Parametry gazów

| Gaz   | Masa `m` | Promień `r` | Kolor         | Liczba startowa |
|-------|----------|-------------|---------------|-----------------|
| Gaz 1 | 1.0      | 4 px        | 🟢 zielony    | 80              |
| Gaz 2 | 4.0      | 7 px        | 🟠 pomarańczowy | 80            |
| Gaz 3 | 10.0     | 12 px       | 🔵 niebieski  | 80              |

---

## 🖥️ Wymagania

```
Python >= 3.8
pygame >= 2.0
```

Instalacja zależności:
```bash
pip install pygame
```

---

## ▶️ Uruchomienie

```bash
git clone https://github.com/wiktorgil/SymulatorGazuIdealnego.git
cd NAZWA_REPO
python main.py
```

---

## 🎮 Sterowanie

| Klawisz | Akcja |
|---------|-------|
| `1` / `2` / `3` | Wybór aktywnego gazu + histogram jego prędkości |
| `G` | Globalny rozkład energii kinetycznej (wszystkie gazy) |
| `↑` / `+` | Dodaj 10 cząstek aktywnego gazu |
| `↓` / `-` | Usuń 10 cząstek aktywnego gazu |
| `W` | Grzanie układu (prędkości ×1.1, energia ×1.21) |
| `S` | Chłodzenie układu (prędkości ×0.9) |

---

## 🔬 Model fizyczny

### Inicjalizacja prędkości
Prędkość startowa każdej cząstki dobierana jest zgodnie z:

```
v = v_base / sqrt(m),    v_base ~ U(2, 6)
```

Analogia prędkości termicznej `v ∝ sqrt(T/m)` — lżejsze cząstki startują szybciej.

### Zderzenia sprężyste między cząstkami
Rozwiązanie analityczne dla zderzenia dwóch dysków wzdłuż osi normalnej `n̂`:

```
q = 2 * (v1 - v2)·n̂ / (m1 + m2)
v1' = v1 - q * m2 * n̂
v2' = v2 + q * m1 * n̂
```

Zachowana jest energia kinetyczna i pęd. Nakładające się cząstki są dodatkowo
odsuwane o połowę głębokości penetracji (zapobieganie „przyklejaniu się").

### Ciśnienie
Obliczane z przekazu pędu do ścian, uśrednionego po ostatnich 60 klatkach:

```
P = <Δp_tot> / (2 * (W + H))
```

Zderzenia między cząstkami **nie wpływają** na obliczane ciśnienie.

### Temperatura (jednostki zredukowane, k_B = 1)
```
T = <Ek> / (N * k_B),    k_B = 1
```

Symulacja używa jednostek zredukowanych - `T` śledzi względne zmiany,
nie jest wartością w kelwinach.

### Gęstość
```
ρ = Σm_i / (W × H)
```

---

## 🗂️ Struktura projektu

```
.
├── main.py          # Główny plik - pętla symulacji, rendering, UI
└── README.md        # Ten plik

```

### Kluczowe funkcje w `main.py`

| Funkcja | Opis |
|---------|------|
| `Particle` | Klasa cząstki — stan (x, y, vx, vy, m, r) + move() + draw() |
| `handle_particle_collisions()` | Zderzenia sprężyste O(N²) |
| `handle_wall_collisions()` | Odbicia od ścian + liczenie przekazu pędu |
| `get_velocity_distribution()` | Histogram prędkości dla wybranego gazu |
| `get_energy_distribution()` | Histogram energii dla wszystkich gazów |
| `get_stats()` | Oblicza T, P, ρ układu |
| `add_particles()` / `remove_particles()` | Dynamiczna zmiana składu |

---

## 📊 Obserwowane zjawiska fizyczne

1. **Maxwell-Boltzmann** — po czasie relaksacji histogram prędkości przyjmuje kształt `f(v) = (mv/kT) * exp(-mv²/2kT)`
2. **Equipartycja** — wszystkie gazy dążą do tej samej średniej energii kinetycznej niezależnie od masy
3. **Prawo Boltzmanna** — globalny rozkład energii zmierza do kształtu eksponencjalnego
4. **Izochoryczna zmiana stanu** — grzanie/chłodzenie przy stałej objętości: `P ∝ T`


---

## 📄 Licencja

MIT — możesz swobodnie używać, modyfikować i rozpowszechniać.
