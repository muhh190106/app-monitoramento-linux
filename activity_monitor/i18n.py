"""English and Brazilian Portuguese messages for the desktop interface."""

MESSAGES = {
    "en": {
        "overview": "Overview", "subtitle": "A clearer view of your time.",
        "tagline": "SCREEN TIME & FOCUS",
        "workspace": "YOUR WORKSPACE", "visitor": "Visitor", "local_profile": "Personal workspace",
        "demo": "Demo workspace", "demo_note": "Sample activity only.\nNo activity is being collected.",
        "language": "Language", "date": "End date", "apply": "Apply",
        "today": "Day", "week": "7 days", "month": "30 days", "all_apps": "All applications",
        "application": "Application", "active": "Active time", "idle": "Idle time",
        "apps": "Applications", "top_app": "Most used app", "timeline": "Activity over time",
        "breakdown": "Application usage", "time": "Time", "share": "Share", "minutes": "Minutes",
        "empty": "No activity for this period", "empty_hint": "Try another date or application.",
        "sample_label": "SAMPLE DATA", "date_error": "Enter a valid date as YYYY-MM-DD.",
        "report_error": "We could not load this view. Please try again.",
        "period": "{start} — {end}", "reset": "Reset filters", "filter_label": "View application",
    },
    "pt-BR": {
        "overview": "Visão geral", "subtitle": "Uma visão mais clara do seu tempo.",
        "tagline": "TEMPO DE TELA E FOCO",
        "workspace": "SEU ESPAÇO", "visitor": "Visitante", "local_profile": "Espaço pessoal",
        "demo": "Espaço demonstrativo", "demo_note": "Apenas dados de exemplo.\nNenhuma atividade está sendo coletada.",
        "language": "Idioma", "date": "Data final", "apply": "Aplicar",
        "today": "Dia", "week": "7 dias", "month": "30 dias", "all_apps": "Todos os aplicativos",
        "application": "Aplicativo", "active": "Tempo ativo", "idle": "Tempo inativo",
        "apps": "Aplicativos", "top_app": "App mais usado", "timeline": "Atividade ao longo do tempo",
        "breakdown": "Uso por aplicativo", "time": "Tempo", "share": "Parcela", "minutes": "Minutos",
        "empty": "Sem atividade neste período", "empty_hint": "Tente outra data ou aplicativo.",
        "sample_label": "DADOS DE EXEMPLO", "date_error": "Informe uma data válida no formato AAAA-MM-DD.",
        "report_error": "Não foi possível carregar esta visão. Tente novamente.",
        "period": "{start} — {end}", "reset": "Limpar filtros", "filter_label": "Ver aplicativo",
    },
}


def translate(language: str, key: str, **values) -> str:
    return MESSAGES[language][key].format(**values)
