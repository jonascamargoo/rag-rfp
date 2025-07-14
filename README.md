# Validador de RFP com RAG e LLMs Locais

Este projeto implementa um protótipo para validar automaticamente os requisitos de uma "Request for Proposal" (RFP) em relação a uma base de conhecimento privada. Utilizando uma arquitetura de Retrieval-Augmented Generation (RAG), a ferramenta é capaz de analisar o texto de uma RFP e determinar se os serviços descritos na base de conhecimento atendem às demandas, fornecendo uma resposta direta e justificada.

A aplicação utiliza modelos de linguagem (LLMs) que rodam localmente através do Ollama, garantindo que nenhum dado sensível da RFP ou da base de conhecimento seja enviado para serviços de terceiros. A interface do utilizador é construída com Streamlit, oferecendo uma experiência simples e intuitiva.

Building...