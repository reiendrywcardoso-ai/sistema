import streamlit as st
import database as db
import email_utils
import time

def render_admin():
    st.markdown("## 🔒 Painel Administrativo")
    st.write("Gerencie acessos e permissões do sistema.")
    
    df_pend = db.get_usuarios_pendentes()
    df_all = db.get_todos_usuarios()
    
    # Cards de Resumo
    c1, c2 = st.columns(2)
    with c1:
        st.markdown(f"""
        <div class="custom-card" style="text-align: center;">
            <h3 style="margin:0; color:#333;">{len(df_all)}</h3>
            <p style="margin:0; color:#666;">Usuários Totais</p>
        </div>
        """, unsafe_allow_html=True)
    with c2:
        st.markdown(f"""
        <div class="custom-card" style="text-align: center;">
            <h3 style="margin:0; color:#d97706;">{len(df_pend)}</h3>
            <p style="margin:0; color:#666;">Aprovações Pendentes</p>
        </div>
        """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["⏳ Pendentes", "👥 Gerenciar Todos"])
    
    with tab1:
        if df_pend.empty:
            st.info("Nenhuma solicitação pendente.")
        else:
            for index, row in df_pend.iterrows():
                with st.container():
                    st.markdown(f"""
                    <div style="background: white; padding: 15px; border-radius: 10px; margin-bottom: 10px; border: 1px solid #e2e8f0; display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="font-weight: bold; color: #333;">{row['username']}</div>
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
        
        st.markdown("### Remover Usuário")
        u_sel = st.selectbox("Selecione:", ["Selecione"] + df_all['username'].tolist())
        
        if u_sel != "Selecione":
            if st.button("🗑️ Remover Acesso"):
                if u_sel == 'admin': st.error("Não pode remover o admin principal.")
                else:
                    db.deletar_usuario(u_sel)
                    st.success("Removido."); time.sleep(1); st.rerun()