import streamlit as st
import database as db
import email_utils
import time

def render_admin():
    st.title("🔒 Painel Administrativo")
    
    tab_pend, tab_todos, tab_criar = st.tabs(["⏳ Pendentes", "👥 Todos / Editar", "➕ Criar Manual"])
    
    with tab_pend:
        df_pend = db.get_usuarios_pendentes()
        if df_pend.empty:
            st.success("Nada pendente.")
        else:
            for index, row in df_pend.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([0.6, 0.2, 0.2])
                    # Mostra o ID gerado
                    c1.write(f"**{row['username']}** (ID: #{row['user_id']})")
                    c1.caption(f"E-mail: {row['email']}")
                    
                    if c2.button("Aprovar ✅", key=f"ap_{row['user_id']}"):
                        db.aprovar_usuario(row['username'])
                        st.success("Aprovado!")
                        if row['email']:
                            email_utils.email_aprovado(
                                row['username'], row['email'], 
                                row['username'], row['password'], 
                                row['user_id']
                            )
                            st.toast("E-mail enviado!")
                        time.sleep(1)
                        st.rerun()
                        
                    if c3.button("Recusar ❌", key=f"dl_{row['user_id']}"):
                        db.deletar_usuario(row['username'])
                        st.rerun()

    with tab_todos:
        df_all = db.get_todos_usuarios()
        st.dataframe(df_all, hide_index=True)
        
        st.markdown("---")
        st.subheader("✏️ Editar Utilizador")
        
        users_list = df_all['username'].tolist() if not df_all.empty else []
        user_to_edit = st.selectbox("Selecione:", ["Selecione"] + users_list)
        
        if user_to_edit != "Selecione":
            row = df_all[df_all['username'] == user_to_edit].iloc[0]
            with st.form("edt_usr"):
                c1, c2 = st.columns(2)
                nu = c1.text_input("Utilizador", value=row['username'])
                ne = c2.text_input("E-mail", value=row['email'])
                np = st.text_input("Senha", value=row['password'], type="password")
                nr = st.selectbox("Cargo", ["user", "admin"], index=0 if row['role']=="user" else 1)
                
                if st.form_submit_button("💾 Salvar"):
                    if db.update_usuario(user_to_edit, {"username":nu, "password":np, "email":ne, "role":nr}):
                        st.success("Atualizado!"); time.sleep(1); st.rerun()
                    else: st.error("Erro.")
            
            if st.button("🗑️ Remover", type="primary"):
                if user_to_edit == 'admin': st.error("Admin fixo não pode ser removido.")
                else: db.deletar_usuario(user_to_edit); st.success("Removido."); time.sleep(1); st.rerun()

    with tab_criar:
        u = st.text_input("Utilizador")
        e = st.text_input("E-mail")
        p = st.text_input("Senha", type="password")
        r = st.selectbox("Cargo", ["user", "admin"])
        if st.button("Criar"):
            res = db.registrar_usuario(u, p, e, r, 1)
            if res['status']: st.success(f"Criado! ID: {res['id_gerado']}")
            else: st.error(res['msg'])