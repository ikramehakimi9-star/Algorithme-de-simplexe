import copy
import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="Méthode du simplexe", page_icon="📐", layout="centered")

# =====================================================
# PARTIE 1 : STYLE GÉNÉRAL (police et cartes)
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
html, body, .stApp, p, label, h1, h2, h3, h4, button, input, textarea {font-family: 'Inter', sans-serif;}
.block-container {padding-top: 2rem; max-width: 900px;}
.entete {border-bottom: 3px solid #0d6efd; padding-bottom: 10px; margin-bottom: 20px;}
.entete h1 {font-size: 2rem; font-weight: 700; margin: 0; color: #0f172a;}
.entete p {margin: 4px 0 0 0; color: #64748b; font-size: 0.95rem;}
div.stButton > button {width: 100%; font-weight: 600; border-radius: 8px; padding: 0.6rem;}
</style>
<div class="entete">
<h1>Méthode du simplexe</h1>
<p>Résolution de programmes linéaires · Outil pédagogique pour étudiants</p>
</div>
""", unsafe_allow_html=True)

# =====================================================
# PARTIE 2 : PARAMÈTRES
# =====================================================
ex_c = [3.0, 2.0]
ex_A = [[2.0, 1.0], [1.0, 2.0]]
ex_b = [6.0, 4.0]

with st.container(border=True):
    st.markdown("**1. Paramètres**")
    col_type, col_n, col_m = st.columns([2, 1, 1])
    type_pb = col_type.radio("Type de problème", ["Maximiser", "Minimiser"], horizontal=True)
    n = col_n.number_input("Variables", min_value=1, max_value=8, value=2, step=1)
    m = col_m.number_input("Contraintes", min_value=1, max_value=8, value=2, step=1)
    exemple = st.checkbox("Charger un exemple (max Z = 3x1 + 2x2 ; 2x1 + x2 ≤ 6 ; x1 + 2x2 ≤ 4)")
    st.caption("Conditions : contraintes de forme ≤, seconds membres b ≥ 0, variables ≥ 0.")

n = int(n)
m = int(m)
suffixe = "_vide"
if exemple:
    suffixe = "_exemple"

# =====================================================
# PARTIE 3 : DONNÉES DU PROBLÈME
# =====================================================
with st.container(border=True):
    st.markdown("**2. Données du problème**")

    st.caption("Fonction objectif Z")
    colonnes = st.columns(n)
    c = []
    for j in range(n):
        defaut = 0.0
        if exemple and j < 2:
            defaut = ex_c[j]
        valeur = colonnes[j].number_input("x" + str(j + 1), value=defaut, step=1.0, format="%g", key="c_" + str(j) + suffixe)
        c.append(valeur)

    A = []
    b = []
    for i in range(m):
        st.caption("Contrainte " + str(i + 1))
        colonnes = st.columns(n + 1)
        ligne = []
        for j in range(n):
            defaut = 0.0
            if exemple and i < 2 and j < 2:
                defaut = ex_A[i][j]
            valeur = colonnes[j].number_input("x" + str(j + 1), value=defaut, step=1.0, format="%g", key="A_" + str(i) + "_" + str(j) + suffixe)
            ligne.append(valeur)
        A.append(ligne)
        defaut = 0.0
        if exemple and i < 2:
            defaut = ex_b[i]
        valeur_b = colonnes[n].number_input("≤ b", value=defaut, step=1.0, format="%g", key="b_" + str(i) + suffixe)
        b.append(valeur_b)

# =====================================================
# PARTIE 4 : APERÇU MATHÉMATIQUE
# =====================================================
lignes_math = [c]
for i in range(m):
    lignes_math.append(A[i])

expressions = []
for r in range(m + 1):
    expr = ""
    for j in range(n):
        coef = lignes_math[r][j]
        if coef != 0:
            if coef < 0 and expr == "":
                signe = "-"
            elif coef < 0:
                signe = " - "
            elif expr == "":
                signe = ""
            else:
                signe = " + "
            if abs(coef) == 1:
                nombre = ""
            else:
                nombre = "%g" % abs(coef)
            expr = expr + signe + nombre + "x_{" + str(j + 1) + "}"
    if expr == "":
        expr = "0"
    expressions.append(expr)

if type_pb == "Maximiser":
    mot = "\\max"
else:
    mot = "\\min"

with st.container(border=True):
    st.markdown("**3. Aperçu du problème**")
    st.latex(mot + " \\; Z = " + expressions[0])
    systeme = "\\begin{cases} "
    for i in range(m):
        systeme = systeme + expressions[i + 1] + " \\le " + "%g" % b[i] + " \\\\ "
    systeme = systeme + "x_{j} \\ge 0, \\; j = 1, \\dots, " + str(n) + " \\end{cases}"
    st.latex(systeme)

lancer = st.button("Résoudre", type="primary")

# =====================================================
# PARTIE 5 : RÉSOLUTION
# =====================================================
if lancer:

    for i in range(m):
        if b[i] < 0:
            st.error("Le b de la contrainte " + str(i + 1) + " est négatif : cette version ne traite que b ≥ 0.")
            st.stop()

    # Minimiser Z revient à maximiser -Z
    c_travail = []
    for j in range(n):
        if type_pb == "Minimiser":
            c_travail.append(-c[j])
        else:
            c_travail.append(c[j])

    # Noms des colonnes : x1, x2... puis e1, e2... (variables d'écart)
    noms = []
    for j in range(n):
        noms.append("x" + str(j + 1))
    for i in range(m):
        noms.append("e" + str(i + 1))

    # Tableau initial
    T = []
    for i in range(m + 1):
        T.append([0.0] * (n + m + 1))
    for i in range(m):
        for j in range(n):
            T[i][j] = A[i][j]
        T[i][n + i] = 1.0
        T[i][n + m] = b[i]
    for j in range(n):
        T[m][j] = c_travail[j]

    base = []
    for i in range(m):
        base.append(n + i)

    titres = []
    entrantes = []
    sortantes = []
    pivots = []
    tableaux = []
    bases = []
    cols = []
    lignes = []
    tab_rapports = []

    optimal = False
    nb_iterations = 0

    for tour in range(50):

        # variable entrante : plus grand coefficient positif de la ligne Z
        maximum = 0.000001
        colonne = -1
        for j in range(n + m):
            if T[m][j] > maximum:
                maximum = T[m][j]
                colonne = j

        if colonne == -1:
            optimal = True
            break

        # variable sortante : plus petit rapport b / coefficient
        minimum = 1e18
        ligne = -1
        rapports = []
        for i in range(m):
            if T[i][colonne] > 0.000001:
                r = T[i][n + m] / T[i][colonne]
                rapports.append("%g" % (round(r, 3) + 0.0))
                if r < minimum:
                    minimum = r
                    ligne = i
            else:
                rapports.append("-")

        if ligne == -1:
            st.error("Le problème est non borné : Z peut augmenter sans limite.")
            st.stop()

        nb_iterations = nb_iterations + 1
        pivot = T[ligne][colonne]

        if nb_iterations == 1:
            titres.append("Tableau initial")
        else:
            titres.append("Itération " + str(nb_iterations - 1))
        entrantes.append(noms[colonne])
        sortantes.append(noms[base[ligne]])
        pivots.append("%g" % (round(pivot, 3) + 0.0))
        tableaux.append(copy.deepcopy(T))
        bases.append(list(base))
        cols.append(colonne)
        lignes.append(ligne)
        tab_rapports.append(rapports)

        # division de la ligne pivot
        for j in range(n + m + 1):
            T[ligne][j] = T[ligne][j] / pivot

        # transformations linéaires
        for i in range(m + 1):
            if i != ligne:
                facteur = T[i][colonne]
                for j in range(n + m + 1):
                    T[i][j] = T[i][j] - facteur * T[ligne][j]

        base[ligne] = colonne

    if optimal == False:
        st.error("Pas de solution trouvée après 50 itérations.")
        st.stop()

    # Dernier tableau (optimal)
    if nb_iterations == 0:
        titres.append("Tableau initial")
    else:
        titres.append("Itération " + str(nb_iterations) + " · tableau final")
    entrantes.append("")
    sortantes.append("")
    pivots.append("")
    tableaux.append(copy.deepcopy(T))
    bases.append(list(base))
    cols.append(-1)
    lignes.append(-1)
    tab_rapports.append(None)

    # Lecture de la solution
    solution = [0.0] * n
    for i in range(m):
        if base[i] < n:
            solution[base[i]] = T[i][n + m]

    Z = 0.0
    for j in range(n):
        Z = Z + c[j] * solution[j]

    if type_pb == "Maximiser":
        nom_z = "Z max"
    else:
        nom_z = "Z min"

    # =====================================================
    # PARTIE 6 : AFFICHAGE DES RÉSULTATS (page Bootstrap)
    # =====================================================
    page = "<!DOCTYPE html><html><head><meta charset='utf-8'>"
    page = page + "<link href='https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css' rel='stylesheet'>"
    page = page + "<link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap' rel='stylesheet'>"
    page = page + "<style>body {font-family: 'Inter', sans-serif; background: transparent; color: #0f172a;} table {font-variant-numeric: tabular-nums;}</style>"
    page = page + "</head><body><div class='container-fluid px-0'>"

    # Carte solution
    page = page + "<div class='card border-primary mb-4'>"
    page = page + "<div class='card-header bg-primary text-white fw-semibold'>Solution optimale</div>"
    page = page + "<div class='card-body'><div class='row text-center g-3'>"
    for j in range(n):
        page = page + "<div class='col'><div class='text-muted small'>x" + str(j + 1) + "</div><div class='fs-3 fw-bold'>" + "%g" % (round(solution[j], 4) + 0.0) + "</div></div>"
    page = page + "<div class='col'><div class='text-muted small'>" + nom_z + "</div><div class='fs-3 fw-bold text-primary'>" + "%g" % (round(Z, 4) + 0.0) + "</div></div>"
    page = page + "</div><div class='text-muted small text-center mt-3'>Obtenue en " + str(nb_iterations) + " itération(s)</div></div></div>"

    page = page + "<h5 class='fw-semibold mb-1'>Étapes détaillées</h5>"
    page = page + "<p class='text-muted small'>e1, e2… sont les variables d'écart. La case en surbrillance est le pivot."
    if type_pb == "Minimiser":
        page = page + " Minimisation : on maximise -Z, la ligne Z concerne donc -Z."
    page = page + "</p>"

    for k in range(len(tableaux)):
        tab = tableaux[k]

        page = page + "<div class='card mb-3'>"
        page = page + "<div class='card-header bg-light fw-semibold'>" + titres[k] + "</div><div class='card-body'>"
        if tab_rapports[k] != None:
            page = page + "<p class='small mb-2'>Variable entrante : <b>" + entrantes[k] + "</b> &nbsp;·&nbsp; Variable sortante : <b>" + sortantes[k] + "</b> &nbsp;·&nbsp; Pivot : <b>" + pivots[k] + "</b></p>"
        else:
            page = page + "<p class='small mb-2'>Plus aucun coefficient positif dans la ligne Z : l'optimum est atteint.</p>"

        page = page + "<div class='table-responsive'><table class='table table-bordered table-sm text-center align-middle mb-0'>"
        page = page + "<thead class='table-light'><tr><th>Base</th>"
        for j in range(n + m):
            page = page + "<th>" + noms[j] + "</th>"
        page = page + "<th>b</th>"
        if tab_rapports[k] != None:
            page = page + "<th>Rapport</th>"
        page = page + "</tr></thead><tbody>"

        for i in range(m):
            page = page + "<tr><th class='table-light'>" + noms[bases[k][i]] + "</th>"
            for j in range(n + m + 1):
                classe = ""
                if i == lignes[k] and j == cols[k]:
                    classe = "table-warning fw-bold"
                page = page + "<td class='" + classe + "'>" + "%g" % (round(tab[i][j], 3) + 0.0) + "</td>"
            if tab_rapports[k] != None:
                page = page + "<td class='text-muted'>" + tab_rapports[k][i] + "</td>"
            page = page + "</tr>"

        page = page + "<tr class='table-secondary'><th>Z</th>"
        for j in range(n + m + 1):
            page = page + "<td>" + "%g" % (round(tab[m][j], 3) + 0.0) + "</td>"
        if tab_rapports[k] != None:
            page = page + "<td></td>"
        page = page + "</tr></tbody></table></div></div></div>"

    # Solution finale
    resume = ""
    for j in range(n):
        resume = resume + "x" + str(j + 1) + " = " + "%g" % (round(solution[j], 4) + 0.0) + " &nbsp;·&nbsp; "
    resume = resume + nom_z + " = " + "%g" % (round(Z, 4) + 0.0)
    page = page + "<div class='alert alert-primary fw-semibold mb-0'>Solution finale : " + resume + "</div>"
    page = page + "</div></body></html>"

    hauteur = 300 + len(tableaux) * ((m + 1) * 42 + 150)

    st.subheader("Résultats")
    components.html(page, height=hauteur, scrolling=True)
