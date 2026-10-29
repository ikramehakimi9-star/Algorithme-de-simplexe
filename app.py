import copy
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Méthode du simplexe", page_icon="📐", layout="wide")

# =====================================================
# PARTIE 1 : TITRE
# =====================================================
st.title("Méthode du simplexe")
st.caption("Résolution de programmes linéaires · Outil pédagogique pour étudiants")
st.divider()

# =====================================================
# PARTIE 2 : PARAMÈTRES (barre latérale)
# =====================================================
st.sidebar.header("Paramètres")
type_pb = st.sidebar.radio("Type de problème", ["Maximiser", "Minimiser"])
exemple = st.sidebar.checkbox("Charger un exemple")
suffixe = "_vide"
if exemple:
    suffixe = "_exemple"
n = st.sidebar.number_input("Nombre de variables", min_value=1, max_value=8, value=2, step=1, key="n" + suffixe)
m = st.sidebar.number_input("Nombre de contraintes", min_value=1, max_value=8, value=2, step=1, key="m" + suffixe)
n = int(n)
m = int(m)
st.sidebar.caption("Conditions : contraintes ≤, seconds membres b ≥ 0, variables ≥ 0.")

ex_c = [3.0, 2.0]
ex_A = [[2.0, 1.0], [1.0, 2.0]]
ex_b = [6.0, 4.0]

# =====================================================
# PARTIE 3 : DONNÉES DU PROBLÈME
# =====================================================
st.subheader("1. Données du problème")

st.markdown("**Fonction objectif Z**")
colonnes = st.columns(n)
c = []
for j in range(n):
    defaut = 0.0
    if exemple and j < 2:
        defaut = ex_c[j]
    valeur = colonnes[j].number_input("x" + str(j + 1), value=defaut, step=1.0, format="%g", key="c_" + str(j) + suffixe)
    c.append(valeur)

st.markdown("**Contraintes**")
A = []
b = []
for i in range(m):
    colonnes = st.columns(n + 1)
    ligne = []
    for j in range(n):
        defaut = 0.0
        if exemple and i < 2 and j < 2:
            defaut = ex_A[i][j]
        valeur = colonnes[j].number_input("x" + str(j + 1) + " · C" + str(i + 1), value=defaut, step=1.0, format="%g", key="A_" + str(i) + "_" + str(j) + suffixe)
        ligne.append(valeur)
    A.append(ligne)
    defaut = 0.0
    if exemple and i < 2:
        defaut = ex_b[i]
    valeur_b = colonnes[n].number_input("≤ b · C" + str(i + 1), value=defaut, step=1.0, format="%g", key="b_" + str(i) + suffixe)
    b.append(valeur_b)

# =====================================================
# PARTIE 4 : APERÇU MATHÉMATIQUE DU PROBLÈME
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

st.markdown("**Aperçu du problème**")
st.latex(mot + " \\; Z = " + expressions[0])
systeme = "\\begin{cases} "
for i in range(m):
    systeme = systeme + expressions[i + 1] + " \\le " + "%g" % b[i] + " \\\\ "
systeme = systeme + "x_{j} \\ge 0, \\; j = 1, \\dots, " + str(n) + " \\end{cases}"
st.latex(systeme)

# =====================================================
# PARTIE 5 : RÉSOLUTION
# =====================================================
if st.button("Résoudre", type="primary"):

    for i in range(m):
        if b[i] < 0:
            st.error("Le b de la contrainte C" + str(i + 1) + " est négatif : cette version ne traite que b ≥ 0.")
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
    textes = []
    tableaux = []
    bases = []
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
                rapports.append(str(round(r, 3) + 0.0))
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
        textes.append("Variable entrante : " + noms[colonne] + "  ·  Variable sortante : " + noms[base[ligne]] + "  ·  Pivot : " + "%g" % (round(pivot, 3) + 0.0))
        tableaux.append(copy.deepcopy(T))
        bases.append(list(base))
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
    textes.append("Optimum atteint : plus aucun coefficient positif dans la ligne Z.")
    tableaux.append(copy.deepcopy(T))
    bases.append(list(base))
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
    # PARTIE 6 : AFFICHAGE (deux onglets)
    # =====================================================
    st.divider()
    st.subheader("2. Résultats")
    onglet_solution, onglet_etapes = st.tabs(["Solution optimale", "Étapes détaillées"])

    with onglet_solution:
        cases = st.columns(n + 1)
        for j in range(n):
            cases[j].metric("x" + str(j + 1), "%g" % (round(solution[j], 4) + 0.0))
        cases[n].metric(nom_z, "%g" % (round(Z, 4) + 0.0))
        st.caption("Solution obtenue en " + str(nb_iterations) + " itération(s).")

    with onglet_etapes:
        st.caption("e1, e2... : variables d'écart. La colonne « Rapport » (b ÷ coefficient de la colonne entrante) désigne la variable sortante.")
        if type_pb == "Minimiser":
            st.caption("Minimisation : on maximise -Z, la ligne Z des tableaux concerne donc -Z.")

        for k in range(len(tableaux)):
            tab = tableaux[k]
            lignes_df = []
            etiquettes = []
            for i in range(m + 1):
                ligne_arrondie = []
                for j in range(n + m + 1):
                    ligne_arrondie.append(round(tab[i][j], 3) + 0.0)
                if tab_rapports[k] != None:
                    if i < m:
                        ligne_arrondie.append(tab_rapports[k][i])
                    else:
                        ligne_arrondie.append("")
                lignes_df.append(ligne_arrondie)
                if i < m:
                    etiquettes.append(noms[bases[k][i]])
                else:
                    etiquettes.append("Z")

            colonnes_df = noms + ["b"]
            if tab_rapports[k] != None:
                colonnes_df = colonnes_df + ["Rapport"]

            st.markdown("**" + titres[k] + "**")
            st.caption(textes[k])
            st.table(pd.DataFrame(lignes_df, columns=colonnes_df, index=etiquettes))

        st.markdown("**Solution finale**")
        resume = ""
        for j in range(n):
            resume = resume + "x" + str(j + 1) + " = " + "%g" % (round(solution[j], 4) + 0.0) + "  ·  "
        resume = resume + nom_z + " = " + "%g" % (round(Z, 4) + 0.0)
        st.success(resume)
