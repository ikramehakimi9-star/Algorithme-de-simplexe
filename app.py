import copy
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Méthode du simplexe", page_icon="📐")

# =====================================================
# PARTIE 1 : TITRE ET MODE D'EMPLOI
# =====================================================
st.title("📐 Méthode du simplexe")
st.write("Résolvez un problème de programmation linéaire et suivez chaque étape.")
st.write("**Comment faire ?** 1) Choisissez le type de problème. 2) Remplissez Z et les contraintes. 3) Cliquez sur **Résoudre**.")
st.caption("Conditions : contraintes de la forme ≤ et seconds membres (b) positifs ou nuls.")

# =====================================================
# PARTIE 2 : SAISIE DU PROBLÈME
# =====================================================
exemple = st.checkbox("Remplir avec un exemple : max Z = 3x1 + 2x2 ; 2x1 + x2 ≤ 6 ; x1 + 2x2 ≤ 4")
ex_c = [3.0, 2.0]
ex_A = [[2.0, 1.0], [1.0, 2.0]]
ex_b = [6.0, 4.0]
suffixe = "_vide"
if exemple:
    suffixe = "_exemple"

type_pb = st.radio("Type de problème", ["Maximiser", "Minimiser"], horizontal=True)

col_n, col_m = st.columns(2)
n = col_n.number_input("Nombre de variables", min_value=1, max_value=8, value=2, step=1, key="n" + suffixe)
m = col_m.number_input("Nombre de contraintes", min_value=1, max_value=8, value=2, step=1, key="m" + suffixe)
n = int(n)
m = int(m)

st.subheader("Fonction objectif Z")
st.caption("Coefficient de chaque variable dans Z.")
colonnes = st.columns(n)
c = []
for j in range(n):
    defaut = 0.0
    if exemple and j < 2:
        defaut = ex_c[j]
    valeur = colonnes[j].number_input("x" + str(j + 1), value=defaut, step=1.0, format="%g", key="c_" + str(j) + suffixe)
    c.append(valeur)

st.subheader("Contraintes")
st.caption("Chaque ligne : coefficients des variables, puis la valeur de b (la contrainte est ≤ b).")
A = []
b = []
for i in range(m):
    colonnes = st.columns(n + 1)
    ligne = []
    for j in range(n):
        defaut = 0.0
        if exemple and i < 2 and j < 2:
            defaut = ex_A[i][j]
        valeur = colonnes[j].number_input("x" + str(j + 1) + " (ligne " + str(i + 1) + ")", value=defaut, step=1.0, format="%g", key="A_" + str(i) + "_" + str(j) + suffixe)
        ligne.append(valeur)
    A.append(ligne)
    defaut = 0.0
    if exemple and i < 2:
        defaut = ex_b[i]
    valeur_b = colonnes[n].number_input("b (ligne " + str(i + 1) + ")", value=defaut, step=1.0, format="%g", key="b_" + str(i) + suffixe)
    b.append(valeur_b)

# =====================================================
# PARTIE 3 : RÉSOLUTION
# =====================================================
if st.button("Résoudre", type="primary"):

    for i in range(m):
        if b[i] < 0:
            st.error("Le b de la ligne " + str(i + 1) + " est négatif. Cette version ne traite que b ≥ 0.")
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

    # On garde chaque tableau pour l'afficher à la fin
    titres = []
    textes = []
    tableaux = []
    bases = []
    tab_rapports = []

    # --- Itérations ---
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
            titres.append("Tableau après l'itération " + str(nb_iterations - 1))
        textes.append("**Variable entrante :** " + noms[colonne] + " (plus grand coefficient positif dans la ligne Z).  \n**Variable sortante :** " + noms[base[ligne]] + " (plus petit rapport).  \n**Pivot :** " + str(round(pivot, 3) + 0.0) + " (ligne " + noms[base[ligne]] + ", colonne " + noms[colonne] + ").")
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
        titres.append("Tableau final après l'itération " + str(nb_iterations))
    textes.append("Tous les coefficients de la ligne Z sont ≤ 0 : **l'optimum est atteint.**")
    tableaux.append(copy.deepcopy(T))
    bases.append(list(base))
    tab_rapports.append(None)

    # --- Lecture de la solution ---
    solution = [0.0] * n
    for i in range(m):
        if base[i] < n:
            solution[base[i]] = T[i][n + m]

    Z = 0.0
    for j in range(n):
        Z = Z + c[j] * solution[j]

    # =====================================================
    # PARTIE 4 : RÉSULTAT
    # =====================================================
    st.header("Résultat")
    texte_solution = ""
    for j in range(n):
        texte_solution = texte_solution + "**x" + str(j + 1) + " = " + str(round(solution[j], 4) + 0.0) + "**  \n"
    if type_pb == "Maximiser":
        texte_solution = texte_solution + "**Z max = " + str(round(Z, 4) + 0.0) + "**"
    else:
        texte_solution = texte_solution + "**Z min = " + str(round(Z, 4) + 0.0) + "**"
    st.success(texte_solution)
    st.write("Solution trouvée en " + str(nb_iterations) + " itération(s).")

    # =====================================================
    # PARTIE 5 : LES TABLEAUX ÉTAPE PAR ÉTAPE
    # =====================================================
    st.header("Détail des étapes")
    st.caption("e1, e2... sont les variables d'écart. La colonne « Rapport » sert à choisir la variable sortante.")
    if type_pb == "Minimiser":
        st.caption("Pour une minimisation, on maximise -Z : la ligne Z des tableaux concerne -Z.")

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

        st.subheader(titres[k])
        st.write(textes[k])
        st.table(pd.DataFrame(lignes_df, columns=colonnes_df, index=etiquettes))
