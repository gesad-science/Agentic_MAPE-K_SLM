import re
import ast
import numpy as np
import pandas as pd

ARQUIVO_LOG = "data/caminho-com-obstaculo-grande-demais.log.txt"
ARQUIVO_CSV = "data/caminho-obstaculo-grande.csv"

# ============================================================
# FUNÇÕES AUXILIARES
# ============================================================

def extrair_vetor(nome, bloco, tamanho):
    m = re.search(
        rf"{re.escape(nome)}\s*:\s*\[([^\]]+)\]",
        bloco
    )

    if not m:
        return [None] * tamanho

    valores = [
        float(x.strip().replace("+", ""))
        for x in m.group(1).split(",")
    ]

    while len(valores) < tamanho:
        valores.append(None)

    return valores[:tamanho]


def extrair_numero(nome, bloco):
    m = re.search(
        rf"{re.escape(nome)}\s*:\s*([-\d\.]+)",
        bloco
    )

    return float(m.group(1)) if m else None


# ============================================================
# LEITURA
# ============================================================

with open(ARQUIVO_LOG, "r", encoding="utf-8") as f:
    texto = f.read()

# ============================================================
# SEPARA CADA STEP
# ============================================================

padrao = re.compile(
    r"Ep\s+(\d+)\s+\|\s+Step\s+(\d+)(.*?)(?=Ep\s+\d+\s+\|\s+Step\s+\d+|$)",
    re.S
)

registros = []

for ep, step, bloco in padrao.findall(texto):

    linha = {
        "episode": int(ep),
        "step": int(step)
    }

    # ========================================================
    # TASK
    # ========================================================

    m = re.search(r"Task\s*:\s*(.+)", bloco)
    linha["task"] = m.group(1).strip() if m else None

    # ========================================================
    # ACTION
    # ========================================================

    action = extrair_vetor("Action", bloco, 4)

    linha["action_x"] = action[0]
    linha["action_y"] = action[1]
    linha["action_z"] = action[2]
    linha["action_gripper"] = action[3]

    # ========================================================
    # EE POSITION
    # ========================================================

    ee = extrair_vetor("EE posição", bloco, 3)

    linha["ee_x"] = ee[0]
    linha["ee_y"] = ee[1]
    linha["ee_z"] = ee[2]

    # ========================================================
    # EE VELOCITY
    # ========================================================

    ee_vel = extrair_vetor("EE velocidade", bloco, 3)

    linha["ee_vx"] = ee_vel[0]
    linha["ee_vy"] = ee_vel[1]
    linha["ee_vz"] = ee_vel[2]

    # ========================================================
    # CUBE POSITION
    # ========================================================

    cube = extrair_vetor("Cubo posição", bloco, 3)

    linha["cube_x"] = cube[0]
    linha["cube_y"] = cube[1]
    linha["cube_z"] = cube[2]

    # ========================================================
    # TARGET ATIVO
    # ========================================================

    target_match = re.search(
        r"Target \(([^)]+)\):\s*\[([^\]]+)\]",
        bloco
    )

    if target_match:

        target_name = target_match.group(1)

        target_pos = [
            float(v.strip().replace("+", ""))
            for v in target_match.group(2).split(",")
        ]

        linha["active_target_name"] = target_name

        if target_name == "target":
            linha["active_target_index"] = 0
        else:
            try:
                linha["active_target_index"] = int(
                    target_name.split("_")[1]
                )
            except:
                linha["active_target_index"] = None

        linha["target_x"] = target_pos[0]
        linha["target_y"] = target_pos[1]
        linha["target_z"] = target_pos[2]

    # ========================================================
    # DISTÂNCIAS
    # ========================================================

    linha["dist_ee_cube"] = extrair_numero(
        "Dist EE→Cubo",
        bloco
    )

    m = re.search(
        r"Dist Cubo→[^:]+:\s*([-\d\.]+)",
        bloco
    )

    linha["dist_cube_target"] = (
        float(m.group(1))
        if m else None
    )

    # ========================================================
    # REWARD
    # ========================================================

    linha["reward"] = extrair_numero(
        "Reward",
        bloco
    )

    # ========================================================
    # SUCCESS
    # ========================================================

    m = re.search(
        r"Sucesso\s*:\s*(True|False)",
        bloco
    )

    linha["success"] = (
        m.group(1) == "True"
        if m else None
    )

    # ========================================================
    # JOINTS
    # ========================================================

    joints = extrair_vetor(
        "Juntas ângulos",
        bloco,
        7
    )

    for i, valor in enumerate(joints):
        linha[f"joint_{i+1}"] = valor

    # ========================================================
    # JOINT VELOCITIES
    # ========================================================

    joints_vel = extrair_vetor(
        "Juntas veloc.",
        bloco,
        7
    )

    for i, valor in enumerate(joints_vel):
        linha[f"joint_vel_{i+1}"] = valor

    # ========================================================
    # CUBE ROTATION
    # ========================================================

    cube_rot = extrair_vetor(
        "Cubo rotação",
        bloco,
        3
    )

    linha["cube_roll"] = cube_rot[0]
    linha["cube_pitch"] = cube_rot[1]
    linha["cube_yaw"] = cube_rot[2]

    # ========================================================
    # CUBE LINEAR VELOCITY
    # ========================================================

    cube_lin = extrair_vetor(
        "Cubo vel.linear",
        bloco,
        3
    )

    linha["cube_vx"] = cube_lin[0]
    linha["cube_vy"] = cube_lin[1]
    linha["cube_vz"] = cube_lin[2]

    # ========================================================
    # TODOS OS TARGETS DO GOAL_SEQUENCE
    # ========================================================

    m = re.search(
        r"Target goal\s*:\s*(\{.*?\})\s*\n",
        bloco,
        re.S
    )

    if m:

        try:
            goal = ast.literal_eval(
                m.group(1)
            )

            targets = goal.get(
                "targets",
                []
            )

            for idx, tgt in enumerate(targets):

                pos = tgt["position"]

                linha[f"goal_{idx}_x"] = pos[0]
                linha[f"goal_{idx}_y"] = pos[1]
                linha[f"goal_{idx}_z"] = pos[2]

                if (
                    cube[0] is not None
                    and cube[1] is not None
                    and cube[2] is not None
                ):

                    dist = np.linalg.norm([
                        cube[0] - pos[0],
                        cube[1] - pos[1],
                        cube[2] - pos[2]
                    ])

                    linha[f"dist_goal_{idx}"] = dist

        except Exception:
            pass

    registros.append(linha)

# ============================================================
# DATAFRAME
# ============================================================

df = pd.DataFrame(registros)

# ============================================================
# DETECTA TROCA DE TARGET
# ============================================================

df["target_changed"] = (
    df["active_target_name"]
    != df["active_target_name"].shift(1)
)

# ============================================================
# TIMESTEP GLOBAL
# ============================================================

df["timestep"] = np.arange(len(df))

# ============================================================
# SALVA CSV
# ============================================================

df.to_csv(
    ARQUIVO_CSV,
    index=False
)

print(f"CSV salvo em: {ARQUIVO_CSV}")
print(df.head())
print(f"\nTotal de registros: {len(df)}")