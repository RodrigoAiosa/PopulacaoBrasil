diff --git a/src/ui/css.py b/src/ui/css.py
index 67fe269..5efc4e4 100644
--- a/src/ui/css.py
+++ b/src/ui/css.py
@@ -118,6 +118,43 @@ section[data-testid="stSidebar"] .stSelectbox[disabled] input {
     color: rgba(255,255,255,0.5) !important;
 }
 
+/* ========================================
+   BOTÃO DE ABRIR/FECHAR A SIDEBAR
+   Sempre visível, com bom contraste sobre o
+   fundo escuro da sidebar e sobre o app.
+   Cobre os diferentes data-testid usados pelo
+   Streamlit em versões distintas.
+   ======================================== */
+[data-testid="stSidebarCollapseButton"],
+[data-testid="stSidebarCollapsedControl"],
+[data-testid="collapsedControl"],
+[data-testid="stSidebarHeader"] button,
+button[kind="header"] {
+    visibility: visible !important;
+    opacity: 1 !important;
+    display: flex !important;
+    pointer-events: auto !important;
+    z-index: 999999 !important;
+}
+
+[data-testid="stSidebarCollapseButton"] svg,
+[data-testid="stSidebarHeader"] button svg {
+    fill: #EAF2EE !important;
+    color: #EAF2EE !important;
+}
+
+[data-testid="stSidebarCollapsedControl"] svg,
+[data-testid="collapsedControl"] svg {
+    fill: var(--primary-dark) !important;
+    color: var(--primary-dark) !important;
+}
+
+[data-testid="stSidebarCollapseButton"]:hover svg,
+[data-testid="stSidebarHeader"] button:hover svg {
+    fill: #FFFFFF !important;
+    color: #FFFFFF !important;
+}
+
 /* ========================================
    BOTÃO DE EXPORTAÇÃO NA SIDEBAR
    ======================================== */
