\NeedsTeXFormat{LaTeX2e}                    % We do need LaTeX2e
\ProvidesClass{pace3dthesis}[2012/04/13 PACE3D Thesis class]

\LoadClass[a4paper, %DIV=9, BCOR=0mm,
  oneside, parskip=half,% Kopf-/Fußzeile, Absatzeinzug
  toc=bibliography]{scrbook} % Class based on scrbook

\newif\ifpacethesis@HS
\pacethesis@HSfalse%
\newif\ifpacethesis@en
\pacethesis@enfalse%

\DeclareOption{HS}{%
\pacethesis@HStrue%
}

\DeclareOption{english}{%
\pacethesis@entrue%
}

\DeclareOption*{%
\PassOptionsToClass{\CurrentOption}{scrbook}%
}
\ProcessOptions\relax

% direct input of unicode chars
\RequirePackage[utf8]{inputenc}
% create searchable PDF files
\RequirePackage{cmap}
\RequirePackage[T1]{fontenc}
\RequirePackage{lmodern}
\RequirePackage{microtype}

\RequirePackage[english,ngerman]{babel}
\ifpacethesis@en
\AtBeginDocument{\selectlanguage{english}}
\fi

\RequirePackage[%
  automark,         % automatische Aktualisierung der Kolumnentitel
  %markcase=ignoreuppercase,      % Grossbuchstaben verhindern
  %markuppercase    % Grossbuchstaben erzwingen
  %markusedcase     % vordefinierten Stil beibehalten
  pagestyleset=KOMA-Script,        % Stil von Koma Script
  %standardstyle,   % Stil der Standardklassen
  headsepline,
]{scrlayer-scrpage}
\pagestyle{scrheadings}
\ohead{\pagemark}
\ihead{\headmark}
\chead{}
\ofoot{}
\ifoot{}
\cfoot{}

\RequirePackage{typearea}
\KOMAoptions{headinclude, headlines=1.1}
\recalctypearea

\renewcommand*{\partpagestyle}{empty}
\renewcommand*{\chapterpagestyle}{empty}

\RequirePackage{graphicx}
\RequirePackage{tikz}
\tikzstyle{every picture}+=[remember picture]
\usetikzlibrary{calc}

\newcommand{\thesis}[1]{\long\def\@thesis{#1}}
\newcommand{\faculty}[1]{\def\@faculty{#1}}
\newcommand{\institute}[1]{\def\@institute{#1}}
\newcommand{\university}[1]{\def\@university{#1}}
\newcommand{\workdate}[1]{\def\@workdate{#1}}

\newcommand{\superone}[1]{\def\@supervisorone{#1}}
\newcommand{\supertwo}[1]{\def\@supervisortwo{#1}}
\newcommand{\superthree}[1]{\def\@supervisorthree{#1}}
\superone{Prof. Dr. rer. nat. Britta Nestler}
\supertwo{M.Sc. Simon Daubner}
\superthree{}

\newcommand{\superonename}[1]{\def\@supervisoronename{#1}}
\newcommand{\supertwoname}[1]{\def\@supervisortwoname{#1}}
\newcommand{\superthreename}[1]{\def\@supervisorthreename{#1}}
\superonename{Institutsleitung}
\supertwoname{Betreuender Mitarbeiter}
\superthreename{Betreuender Mitarbeiter}

\ifpacethesis@HS
  \institute{Institut für Digitale Materialforschung}
  \faculty{}
  \university{Hochschule Karlsruhe -- Technik und Wirtschaft}
  \def\@universityarticlename{der}
\else
  \institute{Institut für Angewandte Materialien\\Computational Materials Science (IAM-CMS)}
  \faculty{Fakultät für Maschinenbau}
  \university{Karlsruher Instituts für Technologie (KIT)}
  \def\@universityarticlename{des}
\fi



\renewcommand{\maketitle}{
\begin{titlepage}
\thispagestyle{empty}

\newlength{\diameter}
\setlength{\diameter}{20pt}
\begin{tikzpicture}[overlay]
  \coordinate (sw) at ($(current page.south west)+(1,1.5)$);
  \coordinate (se) at ($(current page.south east)+(-1,1.5)$);
  \coordinate (nw) at ($(current page.north west)+(1,-1)$);
  \coordinate (ne) at ($(current page.north east)+(-1,-1)$);
  \draw[color=gray] ($(sw)+(0,\diameter)$) |- ($(ne)+(-\diameter,0)$)
  arc (90:0:\diameter)
  |- ($(sw)+(\diameter,0)$)
  arc (270:180:\diameter);
  \node[anchor=north west,inner sep=\diameter] at (nw) {
  \iflanguage{english}
    {\pgfimage[width=0.3\textwidth]{images/kit_logo_en_rgb}}
    {\pgfimage[width=0.3\textwidth]{images/kit_logo_de_rgb}}
  };
  \node[anchor=south west] at ($(sw)+(\diameter,-\diameter)$) {
  \tiny{
  \iflanguage{english}
    {KIT -- University of the State of Baden-Wuerttemberg and National Research Center of the Helmholtz Association}
    {KIT -- Universit\"at des Landes Baden-W\"urttemberg und nationales Forschungszentrum in der Helmholtz-Gemeinschaft}
  }};
  \node[anchor=south east] at ($(se)+(0,-\diameter)$) {
  \large{\textsf{\textbf{www.kit.edu}}
  }};
\end{tikzpicture}

\begin{center}
\hbox{}
\vfill
{\huge\bfseries \@title\par}
\vskip 1.8cm
{\Large\@thesis}\\
\vfill
von\\[2mm]
\vfill

{\Large\bfseries \@author\\}
\vfill
am\\
\vfill
{\large\@institute}\\
\ifx\@faculty\@empty\else%
der\\
{\large\@faculty}\\
\fi
\@universityarticlename\\
{\large\@university}
\vfill\vfill
\begin{tabular}{p{5.5cm}p{5.5cm}}
\ifx\@supervisorone\@empty
\else
\@supervisoronename:   & \@supervisorone\\
\fi%
\ifx\@supervisortwo\@empty
\else
\@supervisortwoname:   & \@supervisortwo\\
\fi%
\ifx\@supervisorthree\@empty
\else
\@supervisorthreename: & \@supervisorthree\\
\fi
\end{tabular}
\vfill
Bearbeitungszeit:\qquad \@workdate

\end{center}
\vfill
\end{titlepage}
}

\newcommand{\affidavit}[1]{
\chapter*{Eidesstattliche Erklärung}%Text nach HS pdf [2012/04/16]
%Hiermit versichere ich, die vorliegende \@thesis{} ohne unzulässige fremde Hilfe selbständig verfasst und keine anderen als die angegebenen Quellen und Hilfsmittel benutzt zu haben.\\[2cm]
%
%Text in pdf Ordnung
Ich erkläre an Eides statt, dass ich die hier vorgelegte \@thesis{} selbstständig und ausschließlich
unter Verwendung der angegebenen Literatur und sonstigen Hilfsmittel verfasst habe. Die Arbeit wurde in gleicher
oder ähnlicher Form keiner anderen Prüfungsbehörde zur Erlangung eines akademischen Grades vorgelegt.\par\vspace{2cm}
#1\par\vspace{2cm}
\@author
}

\AtBeginDocument{
%Set pdf-titel if hyperref is loaded
\@ifpackageloaded{hyperref}{\hypersetup{pdftitle={\@thesis{} von \@author},pdfauthor={\@author}}}{}
}
