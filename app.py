import streamlit as st
from rag_pipeline import create_rag_chain

st.set_page_config(page_title="RFP Validation", layout="wide")
st.title("Validador de Propostas (RFP) com Base de Conhecimento carregada")

try:
    rag_chain = create_rag_chain()
    
    st.info("Base de conhecimento carregada. Insira a demanda da RFP abaixo.")

    user_input = st.text_area("Cole aqui o requisito da RFP para validação:", height=150)

    if st.button("Validar Demanda"):
        if user_input:
            with st.spinner("Analisando..."):
                response = rag_chain.invoke(user_input)
                st.subheader("Resultado da Validação:")
                st.markdown(response)
        else:
            st.warning("Por favor, insira o texto de uma demanda para validar.")

except Exception as e:
    st.error(f"Ocorreu um erro: {e}")