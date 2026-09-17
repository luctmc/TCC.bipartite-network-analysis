"""ETL do OULAD  ``[A]`` — spec A-02.

Open University Learning Analytics Dataset (Kuzilek; Hlosta; Zdrahal,
2017), sete tabelas CSV, ~32 mil estudantes. Download é passo manual
documentado no README; ``download.py`` automatiza e confere o checksum.

O desenvolvimento acontece contra ``tests/data/oulad_mini/`` — sete
arquivos minúsculos com o esquema real —, de modo que a Frente A não
fica bloqueada pelo download de ~450 MB.
"""
