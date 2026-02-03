import streamlit as st
import database as db
import email_utils
import time

def render_admin():
    st.title("🔒 Painel Administrativo")
    
    tab_pend, tab_todos, tab_criar = st.tabs(["⏳ Aprovações Pendentes", "👥 Todos Usuários / Editar", "➕ Criar Acesso"])
    
    with tab_pend:
        df_pend = db.get_usuarios_pendentes()
        if df_pend.empty:
            st.success("Nenhum cadastro pendente.")
        else:
            for index, row in df_pend.iterrows():
                with st.container(border=True):
                    c1, c2, c3 = st.columns([0.6, 0.2, 0.2])
                    c1.write(f"**{row['username']}** (ID: #{row['user_id']})")
                    c1.caption(f"E-mail: {row['email']}")
                    
                    if c2.button("Aprovar ✅", key=f"aprov_{row['username']}"):
                        db.aprovar_usuario(row['username'])
                        st.success(f"Aprovado!")
                        if row['email']:
                            email_utils.email_aprovado(row['username'], row['email'], row['username'], row['password'], row['user_id'])
                            st.toast("E-mail enviado!")
                        time.sleep(1)
                        st.rerun()
                        
                    if c3.button("Recusar ❌", key=f"del_{row['username']}"):
                        db.deletar_usuario(row['username'])
                        st.rerun()

    with tab_todos:
        df_all = db.get_todos_usuarios()
        st.dataframe(df_all, hide_index=True)
        
        st.markdown("---")
        st.subheader("✏️ Editar Usuário")
        
        users_list = df_all['username'].tolist() if not df_all.empty else []
        user_to_edit = st.selectbox("Selecione o Usuário para Editar ou Remover:", ["Selecione"] + users_list)
        
        if user_to_edit != "Selecione":
            # Pega os dados atuais do usuário selecionado
            row = df_all[df_all['username'] == user_to_edit].iloc[0]
            
            with st.form("edit_user_form"):
                st.write(f"Editando: **{user_to_edit}**")
                c1, c2 = st.columns(2)
                # Preenche com os valores atuais
                new_user = c1.text_input("Usuário (Login)", value=row['username'])
                new_email = c2.text_input("E-mail", value=row['email'])
                
                c3, c4 = st.columns(2)
                new_pass = c3.text_input("Senha", value=row['password'], type="password")
                
                # Define o indice do cargo atual
                idx_role = 0 if row['role'] == "user" else 1
                new_role = c4.selectbox("Função", ["user", "admin"], index=idx_role)
                
                col_save, col_del = st.columns([0.8, 0.2])
                
                if col_save.form_submit_button("💾 Salvar Alterações"):
                    if new_user and new_pass and new_email:
                        dados = {
                            "username": new_user,
                            "password": new_pass,
                            "email": new_email,
                            "role": new_role
                        }
                        if db.update_usuario(user_to_edit, dados):
                            st.success("Usuário atualizado com sucesso!")
                            time.sleep(1)
                            st.rerun()
                        else:
                            st.error("Erro ao atualizar.")
                    else:
                        st.warning("Preencha todos os campos.")
            
            # Botão de remover fora do form para evitar submit acidental
            st.markdown("---")
            if st.button(f"🗑️ Remover Usuário {user_to_edit}", type="primary"):
                if user_to_edit == 'admin':
                    st.error("Não pode deletar o admin principal!")
                else:
                    db.deletar_usuario(user_to_edit)
                    st.success("Usuário removido.")
                    time.sleep(1)
                    st.rerun()

    with tab_criar:
        u = st.text_input("Novo Usuário")
        e = st.text_input("E-mail")
        p = st.text_input("Senha", type="password")
        r = st.selectbox("Função", ["user", "admin"])
        if st.button("Criar"):
            res = db.registrar_usuario(u, p, e, r, 1)
            if res['status']: st.success(f"Criado! ID: {res['id_gerado']}")
            else: st.error(res['msg'])