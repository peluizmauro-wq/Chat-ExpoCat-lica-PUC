import re
import unicodedata
from dataclasses import dataclass, field


def _norm(text: str) -> str:
    return unicodedata.normalize("NFKD", str(text)).encode("ascii", "ignore").decode("ascii").lower()


@dataclass
class GuardrailResult:
    allowed: bool
    text: str
    reason: str = ""
    scanners: list = field(default_factory=list)
    redactions: list = field(default_factory=list)


class SecurityGuardrails:
    """Pipeline acadêmico de guardrails de entrada e saída.

    Implementa scanners determinísticos equivalentes aos conceitos de LLM Guard:
    prompt injection, jailbreak, toxicidade/tópicos proibidos e anonimização de PII.
    Também aplica scanner de saída para impedir vazamento de secrets e PII.
    """

    BLOCK_MESSAGE = (
        "Não posso executar esse pedido porque ele tenta contornar as regras de segurança "
        "ou está fora do uso permitido deste Assistente ao Expositor. "
        "Posso ajudar com informações operacionais da ExpoCatólica 2026."
    )

    def __init__(self):
        self.input_scanners = [
            "prompt_injection",
            "jailbreak",
            "toxicidade",
            "topicos_proibidos",
            "pii",
        ]
        self.output_scanners = ["secrets", "pii", "conteudo_interno"]

        self._injection_patterns = [
            r"ignore (todas?|as|os)?\s*(instrucoes|regras|mensagens)",
            r"desconsidere (todas?|as|os)?\s*(instrucoes|regras|mensagens)",
            r"revele (o )?(system prompt|prompt do sistema|instrucoes internas)",
            r"mostre (o )?(system prompt|prompt do sistema|instrucoes internas)",
            r"qual (e|é) (o )?(system prompt|prompt do sistema)",
            r"imprima (as )?(variaveis de ambiente|env|secrets?)",
            r"revele (as )?(variaveis de ambiente|chaves|secrets?)",
        ]
        self._jailbreak_patterns = [
            r"modo dan\b",
            r"developer mode",
            r"sem restricoes",
            r"sem regras",
            r"bypass (de )?(seguranca|safety|filtro)",
            r"jailbreak",
            r"finja que (nao|não) existem regras",
            r"aja como se (nao|não) tivesse regras",
        ]
        self._toxicity_patterns = [
            r"\b(mate|matar|assassinar)\b.{0,40}\b(pessoa|alguem|alguém)\b",
            r"\bameaca(r|s)?\b.{0,30}\b(pessoa|expositor|funcionario|funcionário)\b",
        ]
        self._prohibited_patterns = [
            r"como (fabricar|fazer|montar) (uma |um )?(bomba|explosivo)",
            r"como (invadir|hackear) (uma |um )?(conta|sistema|servidor)",
            r"roubar (senha|credencial|token|chave)",
            r"extrair (senha|credencial|token|chave) de",
        ]

    def _redact_pii(self, text: str):
        redactions = []
        value = str(text)

        patterns = [
            ("email", r"(?<![\w.-])[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}(?![\w.-])", "[EMAIL_PROTEGIDO]"),
            ("cpf", r"(?<!\d)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\d)", "[CPF_PROTEGIDO]"),
            ("cnpj", r"(?<!\d)\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}(?!\d)", "[CNPJ_PROTEGIDO]"),
            ("telefone", r"(?<!\d)(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?9?\d{4}[-\s]?\d{4}(?!\d)", "[TELEFONE_PROTEGIDO]"),
        ]
        for name, pattern, replacement in patterns:
            new_value, count = re.subn(pattern, replacement, value, flags=re.IGNORECASE)
            if count:
                redactions.append(f"{name}:{count}")
                value = new_value
        return value, redactions

    def scan_input(self, text: str) -> GuardrailResult:
        safe_text, redactions = self._redact_pii(text)
        normalized = _norm(safe_text)
        triggered = []

        groups = [
            ("prompt_injection", self._injection_patterns),
            ("jailbreak", self._jailbreak_patterns),
            ("toxicidade", self._toxicity_patterns),
            ("topicos_proibidos", self._prohibited_patterns),
        ]
        for scanner, patterns in groups:
            if any(re.search(p, normalized, flags=re.IGNORECASE) for p in patterns):
                triggered.append(scanner)

        # Limita abuso por prompt excessivamente longo sem afetar perguntas normais.
        if len(safe_text) > 6000:
            triggered.append("prompt_excessivo")

        if triggered:
            return GuardrailResult(
                allowed=False,
                text=self.BLOCK_MESSAGE,
                reason=", ".join(triggered),
                scanners=triggered,
                redactions=redactions,
            )

        scanners = ["pii"] if redactions else []
        return GuardrailResult(
            allowed=True,
            text=safe_text,
            reason="",
            scanners=scanners,
            redactions=redactions,
        )

    def scan_output(self, text: str) -> GuardrailResult:
        safe_text, redactions = self._redact_pii(text)
        scanners = []
        if redactions:
            scanners.append("pii")

        secret_patterns = [
            (r"\bsk-lf-[A-Za-z0-9_-]{8,}\b", "[SECRET_LANGFUSE_PROTEGIDO]"),
            (r"\bpk-lf-[A-Za-z0-9_-]{8,}\b", "[PUBLIC_KEY_PROTEGIDA]"),
            (r"\bsk-[A-Za-z0-9_-]{16,}\b", "[CHAVE_API_PROTEGIDA]"),
        ]
        for pattern, replacement in secret_patterns:
            new_text, count = re.subn(pattern, replacement, safe_text)
            if count:
                safe_text = new_text
                scanners.append("secrets")

        internal_tokens = [
            "OPENAI_API_KEY",
            "LANGFUSE_SECRET_KEY",
        ]
        for token in internal_tokens:
            if token in safe_text:
                safe_text = safe_text.replace(token, "[VARIAVEL_INTERNA_PROTEGIDA]")
                scanners.append("conteudo_interno")

        return GuardrailResult(
            allowed=True,
            text=safe_text,
            reason="",
            scanners=list(dict.fromkeys(scanners)),
            redactions=redactions,
        )
