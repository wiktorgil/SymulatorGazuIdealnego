import pygame
import math
import random

# Ustawienia symulacji
WIDTH, HEIGHT = 1000, 700
FPS = 60

# Konfiguracja gazów
GAS_TYPES = {
    1: {"name": "Gaz 1", "mass": 1.0, "radius": 4, "color": (100, 255, 100)},
    2: {"name": "Gaz 2", "mass": 4.0, "radius": 7, "color": (255, 150, 50)},
    3: {"name": "Gaz 3", "mass": 10.0, "radius": 12, "color": (100, 100, 255)}
}

BG_COLOR = (20, 20, 20)
TEXT_COLOR = (230, 230, 230)

#klasa particle
class Particle:
    def __init__(self, x, y, vx, vy, gas_type_id):
        self.gas_id = gas_type_id
        props = GAS_TYPES[gas_type_id]
        self.mass = props["mass"]
        self.radius = props["radius"]
        self.color = props["color"]
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy

    def move(self):
        self.x += self.vx
        self.y += self.vy

    def draw(self, screen):
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), self.radius)


def add_particles(particles_list, gas_id, amount):
    for _ in range(amount):
        props = GAS_TYPES[gas_id]
        x = random.uniform(props["radius"], WIDTH - props["radius"])
        y = random.uniform(props["radius"], HEIGHT - props["radius"])

        speed_base = random.uniform(2, 6)
        speed = speed_base / math.sqrt(props["mass"])
        angle = random.uniform(0, 2 * math.pi)

        particles_list.append(Particle(x, y, speed * math.cos(angle), speed * math.sin(angle), gas_id))


def remove_particles(particles_list, gas_id, amount):
    removed = 0
    for i in range(len(particles_list) - 1, -1, -1):
        if particles_list[i].gas_id == gas_id:
            particles_list.pop(i)
            removed += 1
            if removed >= amount:
                break


def handle_wall_collisions(particles):
    momentum_transfer = 0.0
    for p in particles:
        if p.x - p.radius <= 0:
            p.x = p.radius
            momentum_transfer += 2.0 * p.mass * abs(p.vx)
            p.vx *= -1
        elif p.x + p.radius >= WIDTH:
            p.x = WIDTH - p.radius
            momentum_transfer += 2.0 * p.mass * abs(p.vx)
            p.vx *= -1

        if p.y - p.radius <= 0:
            p.y = p.radius
            momentum_transfer += 2.0 * p.mass * abs(p.vy)
            p.vy *= -1
        elif p.y + p.radius >= HEIGHT:
            p.y = HEIGHT - p.radius
            momentum_transfer += 2.0 * p.mass * abs(p.vy)
            p.vy *= -1
    return momentum_transfer


def handle_particle_collisions(particles):
    for i in range(len(particles)):
        for j in range(i + 1, len(particles)):
            p1 = particles[i]
            p2 = particles[j]

            dx = p1.x - p2.x
            dy = p1.y - p2.y
            dist_sq = dx ** 2 + dy ** 2
            min_dist = p1.radius + p2.radius

            if dist_sq < min_dist ** 2:
                dist = math.sqrt(dist_sq)
                if dist == 0: continue

                overlap = 0.5 * (min_dist - dist)
                p1.x += (dx / dist) * overlap
                p1.y += (dy / dist) * overlap
                p2.x -= (dx / dist) * overlap
                p2.y -= (dy / dist) * overlap

                nx, ny = dx / dist, dy / dist
                kx = p1.vx - p2.vx
                ky = p1.vy - p2.vy

                p = 2.0 * (nx * kx + ny * ky) / (p1.mass + p2.mass)

                p1.vx -= p * p2.mass * nx
                p1.vy -= p * p2.mass * ny
                p2.vx += p * p1.mass * nx
                p2.vy += p * p1.mass * ny


def get_stats(particles, momentum_history):
    if not particles: return 0, 0, 0

    total_ek = sum(0.5 * p.mass * (p.vx ** 2 + p.vy ** 2) for p in particles)
    KB = 1.0  # jednostki zredukowane (k_B = 1)
    temperature = total_ek / (len(particles) * KB)

    area = WIDTH * HEIGHT
    total_mass = sum(p.mass for p in particles)
    density = total_mass / area

    if momentum_history:
        avg_momentum = sum(momentum_history) / len(momentum_history)
    else:
        avg_momentum = 0.0

    perimeter = 2 * (WIDTH + HEIGHT)
    pressure = avg_momentum / perimeter

    return temperature, density * 1000, pressure * 100


def get_velocity_distribution(particles, gas_id, num_bins=20, max_v=8.0):
    """Kubełkowanie PRĘDKOŚCI dla konkretnego gazu."""
    gas_particles = [p for p in particles if p.gas_id == gas_id]
    bins = [0] * num_bins
    if not gas_particles: return bins
    
    bin_size = max_v / num_bins
    for p in gas_particles:
        v = math.hypot(p.vx, p.vy)
        bin_idx = int(v / bin_size)
        if bin_idx >= num_bins: bin_idx = num_bins - 1
        bins[bin_idx] += 1
    return bins


def get_energy_distribution(particles, num_bins=20, max_e=30.0):
    """Kubełkowanie ENERGII dla wszystkich gazów razem."""
    bins = [0] * num_bins
    if not particles: return bins
    
    bin_size = max_e / num_bins
    for p in particles:
        ek = 0.5 * p.mass * (p.vx ** 2 + p.vy ** 2)
        bin_idx = int(ek / bin_size)
        if bin_idx >= num_bins: bin_idx = num_bins - 1
        bins[bin_idx] += 1
    return bins


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Mieszaniny Gazów Idealnych - Statystyka")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 18)
    title_font = pygame.font.SysFont("consolas", 22, bold=True)

    particles = []
    # Generujemy początkowe cząstki
    add_particles(particles, 1, 80)
    add_particles(particles, 2, 80)
    add_particles(particles, 3, 80)

    momentum_history = []
    selected_gas = 1
    chart_mode = "GLOBAL"  
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1: 
                    selected_gas = 1
                    chart_mode = "GAS1"
                if event.key == pygame.K_2: 
                    selected_gas = 2
                    chart_mode = "GAS2"
                if event.key == pygame.K_3: 
                    selected_gas = 3
                    chart_mode = "GAS3"
                if event.key == pygame.K_g:
                    chart_mode = "GLOBAL"
                if event.key in [pygame.K_PLUS, pygame.K_KP_PLUS, pygame.K_EQUALS, pygame.K_UP]:
                    add_particles(particles, selected_gas, 10)
                if event.key in [pygame.K_MINUS, pygame.K_KP_MINUS, pygame.K_DOWN]:
                    remove_particles(particles, selected_gas, 10)
                if event.key == pygame.K_w:
                    for p in particles:
                        p.vx *= 1.1; p.vy *= 1.1
                if event.key == pygame.K_s:
                    for p in particles:
                        p.vx *= 0.9; p.vy *= 0.9

        for p in particles:
            p.move()

        handle_particle_collisions(particles)
        wall_momentum = handle_wall_collisions(particles)
        momentum_history.append(wall_momentum)
        if len(momentum_history) > 60:
            momentum_history.pop(0)

        temp, density, press = get_stats(particles, momentum_history)
        

        screen.fill(BG_COLOR)
        for p in particles:
            p.draw(screen)

        # Lewy Panel
        ui_panel = pygame.Surface((580, 410))
        ui_panel.set_alpha(100)
        ui_panel.fill((40, 40, 50))
        screen.blit(ui_panel, (10, 10))

        stats_texts = [
            title_font.render("PARAMETRY MAKROSKOPOWE:", True, (255, 255, 100)),
            font.render(f"Temperatura (T): {temp:.2f} [j. sim., k_B=1]", True, TEXT_COLOR),
            font.render(f"Ciśnienie   (P): {press:.2f} j.", True, TEXT_COLOR),
            font.render(f"Gęstość    (rho): {density:.2f} j.", True, TEXT_COLOR),
            font.render(f"Suma cząstek(N): {len(particles)}", True, TEXT_COLOR),
            font.render("", True, TEXT_COLOR),
            title_font.render("STEROWANIE I SKŁAD:", True, (100, 255, 255)),
            font.render("[1/2/3] Edycja gazu + Wykres jego prędkości", True, (150, 150, 150)),
            font.render("[G] Przełącz na Globalny Rozkład Energii", True, (150, 150, 150)),
            font.render("[↑/↓] lub [+/-] Gęstość edytowanego gazu", True, (150, 150, 150)),
            font.render("[W/S] Temperatura układu (grzanie/chłodzenie)", True, (150, 150, 150))
        ]

        y_offset = 15
        for text in stats_texts:
            screen.blit(text, (20, y_offset))
            y_offset += 22

        for g_id, g_props in GAS_TYPES.items():
            count = sum(1 for p in particles if p.gas_id == g_id)
            color = (255, 255, 255) if g_id == selected_gas else (120, 120, 120)
            prefix = ">>" if g_id == selected_gas else "  "

            g_text = font.render(f"{prefix} [{g_id}] {g_props['name']}: {count} szt.", True, color)
            pygame.draw.circle(screen, g_props["color"], (35, y_offset + 10), g_props["radius"])
            screen.blit(g_text, (55, y_offset))
            y_offset += 25

        # Prawy Panel
        chart_x, chart_y = 600, 10
        chart_w, chart_h = 390, 220
        
        ui_chart = pygame.Surface((chart_w, chart_h))
        ui_chart.set_alpha(100)
        ui_chart.fill((40, 40, 50))
        screen.blit(ui_chart, (chart_x, chart_y))
        
        num_bins = 20
        graph_baseline = chart_y + chart_h - 30
        graph_leftline = chart_x + 45
        max_bar_h = chart_h - 75
        bin_w = (chart_w - 65) // num_bins

        if chart_mode == "GLOBAL":
            chart_title = title_font.render("GLOBALNY ROZKŁAD ENERGII", True, (255, 255, 100))
            max_val = 30.0
            bins = get_energy_distribution(particles, num_bins=num_bins, max_e=max_val)
            bar_color = (200, 200, 200)
            x_label = "Energia (j.)"
        else:
            g_id = 1 if chart_mode == "GAS1" else (2 if chart_mode == "GAS2" else 3)
            props = GAS_TYPES[g_id]
            chart_title = title_font.render(f"ROZKŁAD V ({props['name']})", True, props['color'])
            max_val = 8.0
            bins = get_velocity_distribution(particles, g_id, num_bins=num_bins, max_v=max_val)
            bar_color = props['color']
            x_label = "Prędkość (j.)"

        screen.blit(chart_title, (chart_x + 10, chart_y + 10))
        max_count = max(bins) if max(bins) > 0 else 1
        
        #Rysowanie słupków histogramu
        for idx, count in enumerate(bins):
            bar_h = int((count / max_count) * max_bar_h)
            bar_x = graph_leftline + 5 + idx * bin_w
            bar_y = graph_baseline - bar_h
            pygame.draw.rect(screen, bar_color, (bar_x, bar_y, bin_w - 2, bar_h))
            
        pygame.draw.line(screen, (200, 200, 200), (graph_leftline, graph_baseline), (chart_x + chart_w - 10, graph_baseline), 2)
        pygame.draw.line(screen, (200, 200, 200), (graph_leftline, graph_baseline), (graph_leftline, chart_y + 45), 2)
        
        font_sub = pygame.font.SysFont("consolas", 12)
        txt_n_max = font_sub.render(f"{max_count}", True, (200, 200, 200))
        txt_n_mid = font_sub.render(f"{max_count//2}", True, (150, 150, 150))
        txt_n_zero = font_sub.render("0", True, (200, 200, 200))
        txt_y_title = font_sub.render("N", True, (255, 255, 100))
        
        screen.blit(txt_n_max, (graph_leftline - 30, graph_baseline - max_bar_h))
        screen.blit(txt_n_mid, (graph_leftline - 30, graph_baseline - max_bar_h // 2))
        screen.blit(txt_n_zero, (graph_leftline - 15, graph_baseline - 7))
        screen.blit(txt_y_title, (graph_leftline - 15, chart_y + 45))
        
        pygame.draw.line(screen, (200, 200, 200), (graph_leftline - 4, graph_baseline - max_bar_h), (graph_leftline, graph_baseline - max_bar_h), 1)
        pygame.draw.line(screen, (150, 150, 150), (graph_leftline - 4, graph_baseline - max_bar_h // 2), (graph_leftline, graph_baseline - max_bar_h // 2), 1)

        txt_x_zero = font_sub.render("0", True, (200, 200, 200))
        txt_x_max = font_sub.render(f"{max_val:.0f}", True, (200, 200, 200))
        txt_x_title = font_sub.render(x_label, True, (255, 255, 100))
        
        screen.blit(txt_x_zero, (graph_leftline + 2, graph_baseline + 5))
        screen.blit(txt_x_max, (chart_x + chart_w - 25, graph_baseline + 5))
        screen.blit(txt_x_title, (chart_x + chart_w // 2 - 30, graph_baseline + 15))

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    main()