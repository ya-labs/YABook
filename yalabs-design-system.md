# 🎨 YA LABS - Design System

> Sistema oficial de identidade visual da YA LABS.
>
> **Slogan:** Code. Automate. Scale.

---

# Filosofia da Marca

A YA LABS é construída sobre os pilares de:

- Engenharia
- Automação
- Escalabilidade
- Simplicidade
- Profissionalismo

A identidade visual prioriza alto contraste, interfaces limpas e uma aparência tecnológica moderna.

---

# Cores Principais

## Cor Primária

<div style="width:220px">

<div style="
height:140px;
background:#0A1A5E;
border-radius:16px;
">
</div>

### YA Dark Blue

`#0A1A5E`

Cor principal da organização.

</div>

---

## Cor de Destaque

<div style="width:220px">

<div style="
height:140px;
background:#2563FF;
border-radius:16px;
">
</div>

### YA Blue

`#2563FF`

Utilizada para ações, destaques e elementos interativos.

</div>

---

## Branco

<div style="width:220px">

<div style="
height:140px;
background:#FFFFFF;
border:1px solid #DDE3EA;
border-radius:16px;
">
</div>

### White

`#FFFFFF`

Cor principal para fundos em interfaces claras.

</div>

---

# Tema Claro

Tema padrão para:

- Site institucional
- Documentação
- Landing pages
- Apresentações
- Materiais de divulgação

<div style="display:flex;gap:20px;flex-wrap:wrap;">

<div>
<div style="width:120px;height:120px;background:#FFFFFF;border:1px solid #DDD;border-radius:12px;"></div>

Background

`#FFFFFF`
</div>

<div>
<div style="width:120px;height:120px;background:#F8FAFC;border-radius:12px;"></div>

Surface

`#F8FAFC`
</div>

<div>
<div style="width:120px;height:120px;background:#0A1A5E;border-radius:12px;"></div>

Primária

`#0A1A5E`
</div>

<div>
<div style="width:120px;height:120px;background:#2563FF;border-radius:12px;"></div>

Destaque

`#2563FF`
</div>

<div>
<div style="width:120px;height:120px;background:#0F172A;border-radius:12px;"></div>

Texto

`#0F172A`
</div>

</div>

---

# Tema Escuro

Tema padrão para:

- Dashboards
- Ferramentas internas
- Plataformas de desenvolvimento
- Painéis administrativos

<div style="display:flex;gap:20px;flex-wrap:wrap;">

<div>
<div style="width:120px;height:120px;background:#0F172A;border-radius:12px;"></div>

Background

`#0F172A`
</div>

<div>
<div style="width:120px;height:120px;background:#111827;border-radius:12px;"></div>

Surface

`#111827`
</div>

<div>
<div style="width:120px;height:120px;background:#FFFFFF;border:1px solid #DDD;border-radius:12px;"></div>

Primária

`#FFFFFF`
</div>

<div>
<div style="width:120px;height:120px;background:#2563FF;border-radius:12px;"></div>

Destaque

`#2563FF`
</div>

<div>
<div style="width:120px;height:120px;background:#CBD5E1;border-radius:12px;"></div>

Texto

`#CBD5E1`
</div>

</div>

---

# Cores de Status

<div style="display:flex;gap:20px;flex-wrap:wrap;">

<div>
<div style="width:120px;height:120px;background:#22C55E;border-radius:12px;"></div>

Sucesso

`#22C55E`
</div>

<div>
<div style="width:120px;height:120px;background:#F59E0B;border-radius:12px;"></div>

Aviso

`#F59E0B`
</div>

<div>
<div style="width:120px;height:120px;background:#EF4444;border-radius:12px;"></div>

Erro

`#EF4444`
</div>

<div>
<div style="width:120px;height:120px;background:#0EA5E9;border-radius:12px;"></div>

Informação

`#0EA5E9`
</div>

</div>

---

# Gradiente Oficial

<div
style="
height:180px;
border-radius:16px;
background:linear-gradient(
135deg,
#0A1A5E 0%,
#1639B5 50%,
#2563FF 100%
);
">
</div>

```css
background: linear-gradient(
    135deg,
    #0A1A5E 0%,
    #1639B5 50%,
    #2563FF 100%
);
```

---

# Variáveis CSS

```css
:root {

    /* Marca */

    --ya-primary: #0A1A5E;
    --ya-accent: #2563FF;

    /* Tema Claro */

    --ya-background: #FFFFFF;
    --ya-surface: #F8FAFC;

    --ya-text: #0F172A;
    --ya-text-muted: #64748B;

    /* Status */

    --ya-success: #22C55E;
    --ya-warning: #F59E0B;
    --ya-error: #EF4444;
    --ya-info: #0EA5E9;
}
```

---

# Diretrizes de Uso

## Distribuição Recomendada

```txt
70% Branco
20% YA Dark Blue
10% YA Blue
```

## Utilizar YA Dark Blue em

- Cabeçalhos
- Navegação
- Branding
- Logotipos
- Seções importantes
- Rodapés

## Utilizar YA Blue em

- Botões
- Links
- Estados de hover
- Elementos interativos
- Destaques

## Utilizar Branco em

- Fundos principais
- Áreas de leitura
- Documentação
- Páginas de conteúdo

---

# Governança de Design

O Design System da YA LABS existe para criar consistência entre os projetos do ecossistema.

Os projetos são incentivados a utilizar:

- Cores da YA LABS
- Padrões tipográficos
- Princípios de layout
- Componentes compartilhados
- Diretrizes de acessibilidade

Entretanto, o Design System não é obrigatório para todos os projetos.

---

# Exceções de Design

Alguns projetos podem intencionalmente divergir da identidade visual da YA LABS.

Motivos incluem:

- Conceitos experimentais
- Projetos de estudo
- Ferramentas comunitárias
- Aplicações voltadas para jogos
- Eventos específicos
- Produtos independentes

Nesses casos, o projeto pode definir sua própria:

- Paleta de cores
- Tipografia
- Linguagem visual
- Identidade de marca
- Experiência de usuário

desde que continue alinhado aos valores da YA LABS.

---

# Classificação de Projetos

## Projetos Principais

Projetos estratégicos que representam diretamente a YA LABS.

Devem seguir o Design System oficial.

Exemplos:

- YABook
- DevLab
- Git2SVN
- YA HUB
- Plataformas Internas
- Produtos corporativos futuros

---

## Projetos Independentes

Projetos que podem possuir identidade visual própria.

Exemplos:

- CADE O DANO
- Projetos de Hackathon
- Produtos Experimentais
- Ferramentas Comunitárias
- Projetos de Entretenimento

Esses projetos podem adotar uma identidade visual completamente diferente quando isso fizer mais sentido para seus objetivos.

---

# Princípio Fundamental

Consistência é desejável.

Propósito tem prioridade.

Um projeto nunca deve sacrificar sua identidade apenas para seguir o padrão visual da organização.

---

# Idioma Oficial

O idioma padrão da YA LABS é:

**Português (Brasil)**

Exceções:

- Projetos com público internacional
- Projetos open source globais
- Produtos destinados a usuários não falantes de português
- Documentações específicas para mercados internacionais

---

# Cores Oficiais da Marca

Primária

`#0A1A5E`

Destaque

`#2563FF`

Fundo

`#FFFFFF`

---

# Slogan Oficial

**Code. Automate. Scale.**