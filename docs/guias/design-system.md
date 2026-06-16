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

# Papel do YAHub

O YAHub deve ser tratado como a principal referência visual institucional da YA LABS.

Ele representa a experiência de entrada do ecossistema: portal, apresentação da organização, acesso a projetos, documentação, materiais internos e pontos de navegação entre produtos.

Por isso, o YAHub pode usar mais respiro visual, composição institucional, seções de apresentação e elementos de marca do que uma ferramenta operacional.

O design system deve nascer observando o YAHub, mas não deve copiar literalmente cada decisão de layout para todos os produtos.

---

# Portal e Aplicações

A identidade visual da YA LABS deve ser compartilhada entre os projetos, mas cada tipo de experiência precisa adaptar essa identidade ao seu contexto.

## YAHub

O YAHub deve priorizar:

- primeira impressão da marca;
- clareza institucional;
- navegação entre projetos e recursos;
- apresentação visual mais aberta;
- comunicação dos valores da YA LABS;
- organização de links, guias e pontos de acesso.

## Aplicações e Ferramentas

Aplicações como o SVNFlow devem herdar a identidade da YA LABS, mas priorizar:

- produtividade;
- leitura rápida;
- estados operacionais claros;
- feedback para ações sensíveis;
- densidade maior de informação;
- navegação objetiva;
- componentes voltados ao uso recorrente.

Na prática, o YAHub define a linguagem visual principal, enquanto aplicações desktop e ferramentas internas adaptam essa linguagem para fluxos de trabalho.

---

# Uso de Referências Visuais

Referências externas podem ser usadas para amadurecer o design system, desde que sirvam como inspiração e não como cópia direta.

Ao avaliar uma referência, observe:

- sensação transmitida pela interface;
- organização de navegação;
- uso de tipografia;
- hierarquia visual;
- tratamento de cards, listas, formulários e botões;
- equilíbrio entre identidade visual e clareza;
- adaptação possível para portal, documentação e aplicações.

Depois de analisar referências, registre somente decisões aplicáveis à YA LABS.

Exemplo:

```text
Referência observada: portal com navegação lateral clara e cards objetivos.
Decisão para YA LABS: usar navegação simples e cards informativos no YAHub.
Adaptação para apps: usar listas e painéis mais densos em ferramentas como SVNFlow.
```

---

# Processo de Evolução do Design System

O design system da YA LABS deve evoluir a partir de uso real, não de regras visuais definidas no vazio.

O fluxo recomendado é:

1. Coletar referências visuais externas.
2. Identificar o que cada referência tem de útil para a YA LABS.
3. Transformar as referências em direção visual própria.
4. Aplicar a direção visual primeiro no YAHub.
5. Revisar o resultado com olhar crítico de hierarquia, contraste, espaçamento, tipografia e clareza.
6. Extrair padrões reutilizáveis para o design system.
7. Adaptar esses padrões para aplicações e ferramentas internas.
8. Registrar no YABook apenas decisões estáveis e reutilizáveis.

## Papel do YAHub no Processo

O YAHub deve ser o primeiro produto usado para validar a identidade visual da YA LABS.

Ele serve como base para testar:

- linguagem visual;
- paleta de cores;
- tipografia;
- navegação;
- cards;
- seções institucionais;
- apresentação de projetos;
- tom visual da marca.

Depois que uma decisão funcionar bem no YAHub, ela pode ser registrada como padrão organizacional.

## Papel do SVNFlow e Aplicações Desktop

O SVNFlow não deve copiar o layout do YAHub diretamente.

Ele deve usar a mesma identidade visual, mas com ajustes para uma ferramenta de trabalho:

- menos decoração;
- maior densidade de informação;
- feedback operacional mais explícito;
- ações principais mais evidentes;
- estados de erro, aviso e sucesso bem definidos;
- navegação voltada ao uso frequente.

Essa separação evita transformar um app desktop em landing page e evita que o portal fique com aparência de sistema administrativo.

## Uso do Impeccable

O Impeccable é a skill de design recomendada para apoiar a criação e evolução visual dos projetos da YA LABS no Codex.

Ele deve ser usado para apoiar auditoria visual, refinamento de interface e melhoria de consistência.

O fluxo recomendado é:

1. Rodar `/impeccable init` no projeto que receberá o design.
2. Definir o contexto do produto, público, intenção visual e restrições.
3. Usar `/impeccable shape` antes de implementar telas novas.
4. Usar `/impeccable critique` para avaliar a experiência e a direção visual.
5. Usar `/impeccable audit` para checar qualidade técnica, acessibilidade e responsividade.
6. Usar `/impeccable polish` antes de considerar a interface pronta.
7. Usar `/impeccable extract` quando uma decisão visual puder virar token, componente ou regra reutilizável.

O Impeccable deve ajudar a avaliar e melhorar:

- hierarquia visual;
- contraste;
- espaçamento;
- tipografia;
- alinhamento;
- estados de interação;
- acessibilidade;
- excesso de elementos decorativos;
- aparência genérica de interface criada por IA.

Ele não substitui a direção visual da YA LABS.

A intenção da marca deve ser definida primeiro. Depois disso, o Impeccable ajuda a transformar essa intenção em uma interface mais consistente e profissional.

Se outro recurso de design for usado no futuro, ele deve seguir a mesma regra: apoiar o processo, não definir sozinho a identidade visual.

## Registro das Decisões

Nem toda experimentação deve virar padrão oficial.

Registre no design system apenas decisões que:

- foram aplicadas em uma interface real;
- melhoraram clareza ou consistência;
- podem ser reutilizadas em mais de um projeto;
- não dependem de um produto específico;
- ajudam outros projetos da YA LABS a tomar decisões parecidas.

Decisões específicas de produto devem ficar no repositório do próprio produto.

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
