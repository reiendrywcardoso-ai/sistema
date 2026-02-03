import streamlit as st
import database as db
import email_utils
import time

def render_admin():
    st.markdown("## Painel Administrativo")
    st.write("Controle de acessos e permissões.")
    
    df_pend = db.get_usuarios_pendentes()
    df_all = db.get_todos_usuarios()
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="dashboard-card" style="text-align: center;">
            <div style="font-size: 32px; font-weight: 700; color: #1e293b;">{len(df_all)}</div>
            <div style="color: #64748b; font-size: 14px;">Usuários Totais</div>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="dashboard-card" style="text-align: center;">
            <div style="font-size: 32px; font-weight: 700; color: #f59e0b;">{len(df_pend)}</div>
            <div style="color: #64748b; font-size: 14px;">Pendentes</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("")
    tab1, tab2 = st.tabs(["Aprovações", "Gerenciar"])
    
    with tab1:
        if df_pend.empty:
            st.info("Nenhuma solicitação pendente.")
        else:
            for index, row in df_pend.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div class="dashboard-card" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
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
    
    with tab2:
        st.dataframe(df_all, use_container_width=True, hide_index=True)
        st.markdown("### Remover Acesso")
        u_sel = st.selectbox("Selecione:", ["Selecione"] + df_all['username'].tolist())
        
        if u_sel != "Selecione":
            if st.button("🗑️ Remover"):
                if u_sel == 'admin': st.error("Admin fixo.")
                else:
                    db.deletar_usuario(u_sel)
                    st.success("Removido."); time.sleep(1); st.rerun()