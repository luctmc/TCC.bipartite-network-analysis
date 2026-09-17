"""
Gera um dataset sintético no formato do OULAD para testar o pipeline
localmente, sem depender do download do dataset real.

Uso:
    python generate_synthetic.py

Gera data/synthetic/studentInfo.csv com colunas:
    id_student, code_module, code_presentation, final_result, score_media

O gerador planta comunidades conhecidas de propósito (grupos de alunos
com preferência por conjuntos de módulos distintos), para servir como
"ground truth" na validação do Louvain/Girvan-Newman (ver src/community).
"""
import random
import csv
import os

random.seed(42)

MODULES = {
    # cada grupo de módulos representa uma "área" -- usado só para plantar estrutura
    "exatas":   ["AAA", "BBB", "CCC"],
    "sistemas": ["DDD", "EEE"],
    "humanas":  ["FFF", "GGG"],
}
ALL_MODULES = [m for grupo in MODULES.values() for m in grupo]

N_STUDENTS_PER_GROUP = 40
PRESENTATIONS = ["2024J", "2024B"]


def gen_student(sid, grupo_nome, grupo_modulos, risco):
    """Gera as matrículas de um estudante, enviesadas para o seu grupo."""
    rows = []
    # 2 a 4 módulos do próprio grupo (alta afinidade)
    n_in = random.randint(2, min(4, len(grupo_modulos)))
    for m in random.sample(grupo_modulos, k=n_in):
        rows.append((m, risco))
    # 0 a 1 módulo de fora do grupo (ruído -- impede comunidades perfeitas)
    if random.random() < 0.35:
        outros = [m for m in ALL_MODULES if m not in grupo_modulos]
        rows.append((random.choice(outros), risco))

    out = []
    for module, r in rows:
        presentation = random.choice(PRESENTATIONS)
        # aluno "em risco" tende a nota mais baixa e mais chance de Withdrawn
        if r:
            score = max(0, min(100, random.gauss(48, 14)))
            final_result = random.choices(
                ["Pass", "Fail", "Withdrawn"], weights=[0.35, 0.30, 0.35]
            )[0]
        else:
            score = max(0, min(100, random.gauss(72, 12)))
            final_result = random.choices(
                ["Pass", "Distinction", "Fail", "Withdrawn"],
                weights=[0.55, 0.20, 0.15, 0.10],
            )[0]
        out.append(
            {
                "id_student": sid,
                "code_module": module,
                "code_presentation": presentation,
                "final_result": final_result,
                "score_media": round(score, 1),
            }
        )
    return out


def main():
    rows = []
    sid = 100000
    for grupo_nome, grupo_modulos in MODULES.items():
        for _ in range(N_STUDENTS_PER_GROUP):
            sid += 1
            risco = random.random() < 0.30  # 30% dos alunos de cada grupo em risco
            rows.extend(gen_student(sid, grupo_nome, grupo_modulos, risco))

    os.makedirs("data/synthetic", exist_ok=True)
    path = "data/synthetic/studentInfo.csv"
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id_student",
                "code_module",
                "code_presentation",
                "final_result",
                "score_media",
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Gerado {len(rows)} matrículas de {sid - 100000} estudantes em {path}")


if __name__ == "__main__":
    main()
