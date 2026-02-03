import streamlit as st
import database as db
import email_utils
import time

def render_admin():
    st.markdown("## 🔒 Painel Administrativo")
    st.write("Controle de acessos e permissões.")
    
    df_pend = db.get_usuarios_pendentes()
    df_all = db.get_todos_usuarios()
    
    # Cards de Resumo
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="react-card" style="text-align: center;">
            <div style="font-size: 32px; font-weight: 700; color: #1e293b;">{len(df_all)}</div>
            <div style="color: #64748b; font-size: 14px;">Usuários Totais</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="react-card" style="text-align: center;">
            <div style="font-size: 32px; font-weight: 700; color: #f59e0b;">{len(df_pend)}</div>
            <div style="color: #64748b; font-size: 14px;">Pendentes</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    # ABA CRIAR ACESSO RESTAURADA AQUI
    tab1, tab2, tab3 = st.tabs(["⏳ Pendentes", "👥 Gerenciar / Editar", "➕ Criar Acesso"])
    
    with tab1:
        if df_pend.empty:
            st.info("Nenhuma solicitação pendente.")
        else:
            for index, row in df_pend.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div style="background: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: 600; color: #1e293b;">{row['username']}</div>
                            <div style="color: #64748b; font-size: 13px;">{row['email']}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    b1, b2 = st.columns([1, 4])
                    if b1.button("Aprovar", key=f"ap_{row['user_id']}", type="primary"):
                        db.aprovar_usuario(row['username'])
                        if row['email']:
                            email_utils.email_aprovado(row['username'], row['email'], row['username'], row['password'], row['user_id'])
                        st.success("Aprovado!"); time.sleep(1); st.rerun()
                    if b2.button("Recusar", key=f"rec_{row['user_id']}"):
                        db.deletar_usuario(row['username'])
                        st.rerun()
    
    # ABA GERENCIAR COM EDIÇÃO (RESTAURADA)
    with tab2:
        st.dataframe(df_all, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("### ✏️ Editar / Remover Usuário")
        
        u_sel = st.selectbox("Selecione:", ["Selecione"] + df_all['username'].tolist())
        
        if u_sel != "Selecione":
            row_u = df_all[df_all['username'] == u_sel].iloc[0]
            
            with st.container():
                st.markdown('<div class="react-card">', unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                nu = c1.text_input("Login", value=row_u['username'])
                ne = c2.text_input("E-mail", value=row_u['email'])
                np = c1.text_input("Senha", value=row_u['password'], type="password")
                nr = c2.selectbox("Função", ["user", "admin"], index=0 if row_u['role']=="user" else 1)
                
                if st.button("Salvar Alterações"):
                    db.update_usuario(u_sel, {"username": nu, "password": np, "email": ne, "role": nr})
                    st.success("Usuário Atualizado!"); time.sleep(1); st.rerun()
                
                st.markdown("---")
                if st.button("🗑️ Remover Acesso"):
                    if u_sel == 'admin': st.error("Não pode remover o admin principal.")
                    else:
                        db.deletar_usuario(u_sel)
                        st.success("Removido."); time.sleep(1); st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)

    # ABA CRIAR ACESSO (MANUAL) - RESTAURADA
    with tab3:
        st.markdown('<div class="react-card">', unsafe_allow_html=True)
        st.write("Criar um usuário manualmente (já aprovado).")
        
        c_new1, c_new2 = st.columns(2)
        new_u = c_new1.text_input("Novo Usuário")
        new_e = c_new2.text_input("Novo E-mail")
        new_p = c_new1.text_input("Nova Senha", type="password")
        new_r = c_new2.selectbox("Função", ["user", "admin"])
        
        if st.button("Criar Usuário"):
            res = db.registrar_usuario(new_u, new_p, new_e, new_r, approved=1)
            if res['status']:
                st.success(f"Criado com sucesso! ID: {res['id_gerado']}")
            else:
                st.error(res['msg'])
        st.markdown('</div>', unsafe_allow_html=True)