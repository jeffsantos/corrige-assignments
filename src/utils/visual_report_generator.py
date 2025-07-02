"""
Gerador de relatórios visuais com thumbnails de dashboards Streamlit.
"""
from pathlib import Path
from typing import List
from ..domain.models import ThumbnailResult, CorrectionReport


class VisualReportGenerator:
    """Gerador de relatórios visuais com thumbnails."""
    
    def generate_visual_report(self, assignment_name: str, turma_name: str, 
                             thumbnails: List[ThumbnailResult], 
                             correction_report: CorrectionReport,
                             output_dir: Path) -> Path:
        """Gera relatório visual HTML com thumbnails organizados."""
        
        # Organiza thumbnails por nota (decrescente)
        submissions_with_thumbnails = []
        for submission in correction_report.submissions:
            # Encontra thumbnail correspondente
            thumbnail = next((t for t in thumbnails if t.submission_identifier == 
                            (getattr(submission, 'github_login', None) or getattr(submission, 'group_name', None))), None)
            
            submissions_with_thumbnails.append({
                'submission': submission,
                'thumbnail': thumbnail
            })
        
        # Ordena por nota decrescente
        submissions_with_thumbnails.sort(key=lambda x: x['submission'].final_score, reverse=True)
        
        # Gera HTML
        html_content = self._build_visual_html(
            assignment_name, turma_name, submissions_with_thumbnails, correction_report
        )
        
        # Salva arquivo
        output_file = output_dir / f"{assignment_name}_{turma_name}_visual.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file
    
    def _build_visual_html(self, assignment_name: str, turma_name: str,
                          submissions_with_thumbnails: List[dict],
                          correction_report: CorrectionReport) -> str:
        """Constrói o HTML do relatório visual."""
        
        # Gera grid de thumbnails
        thumbnails_html = ""
        for item in submissions_with_thumbnails:
            submission = item['submission']
            thumbnail = item['thumbnail']
            
            # Determina status baseado na nota
            if submission.final_score >= 9.0:
                status_class = "excellent"
                status_icon = "🟢"
                status_text = "Excelente"
            elif submission.final_score >= 7.0:
                status_class = "good"
                status_icon = "🟡"
                status_text = "Bom"
            elif submission.final_score >= 6.0:
                status_class = "pass"
                status_icon = "🟠"
                status_text = "Aprovado"
            else:
                status_class = "fail"
                status_icon = "🔴"
                status_text = "Reprovado"
            
            # Informações dos testes
            test_info = "N/A"
            if submission.test_results:
                passed = sum(1 for test in submission.test_results if test.result.value == "passed")
                total = len(submission.test_results)
                test_info = f"{passed}/{total}"
            
            # Thumbnail ou placeholder
            if thumbnail and thumbnail.streamlit_status == "success" and thumbnail.thumbnail_path.exists():
                thumbnail_src = f"thumbnails/{thumbnail.thumbnail_path.name}"
                thumbnail_alt = f"Dashboard de {submission.display_name}"
            else:
                thumbnail_src = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkRhc2hib2FyZCBuw6NvIGRpc3BvbsOtdmVsPC90ZXh0Pjwvc3ZnPg=="
                thumbnail_alt = "Dashboard não disponível"
            
            thumbnails_html += f"""
            <div class="thumbnail-card {status_class}">
                <div class="thumbnail-header">
                    <h3>{submission.display_name}</h3>
                    <div class="score-badge {status_class}">
                        {status_icon} {submission.final_score:.1f}/10
                    </div>
                </div>
                <div class="thumbnail-image">
                    <img src="{thumbnail_src}" alt="{thumbnail_alt}" onclick="showDetails('{submission.display_name}', {submission.final_score}, '{test_info}', '{status_text}')">
                </div>
                <div class="thumbnail-info">
                    <div class="status">{status_icon} {status_text}</div>
                    <div class="tests">🧪 {test_info}</div>
                    <div class="timestamp">{thumbnail.capture_timestamp[:19] if thumbnail else 'N/A'}</div>
                </div>
            </div>
            """
        
        return f"""
<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Relatório Visual - {assignment_name}</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }}
        
        .header h1 {{
            font-size: 2.5em;
            margin-bottom: 10px;
        }}
        
        .header p {{
            font-size: 1.2em;
            opacity: 0.9;
        }}
        
        .summary {{
            background: #f8f9fa;
            padding: 25px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .summary-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }}
        
        .summary-item {{
            background: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        
        .summary-item h3 {{
            color: #667eea;
            font-size: 2em;
            margin-bottom: 5px;
        }}
        
        .summary-item p {{
            color: #6c757d;
            font-weight: 500;
        }}
        
        .thumbnails-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
            gap: 25px;
            padding: 30px;
        }}
        
        .thumbnail-card {{
            background: white;
            border-radius: 15px;
            overflow: hidden;
            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
            cursor: pointer;
        }}
        
        .thumbnail-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        
        .thumbnail-header {{
            padding: 20px;
            background: #f8f9fa;
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .thumbnail-header h3 {{
            font-size: 1.1em;
            color: #495057;
            margin: 0;
        }}
        
        .score-badge {{
            padding: 8px 15px;
            border-radius: 20px;
            font-weight: bold;
            font-size: 0.9em;
        }}
        
        .score-badge.excellent {{
            background: #d4edda;
            color: #155724;
        }}
        
        .score-badge.good {{
            background: #d1ecf1;
            color: #0c5460;
        }}
        
        .score-badge.pass {{
            background: #fff3cd;
            color: #856404;
        }}
        
        .score-badge.fail {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .thumbnail-image {{
            position: relative;
            overflow: hidden;
        }}
        
        .thumbnail-image img {{
            width: 100%;
            height: 250px;
            object-fit: cover;
            transition: transform 0.3s ease;
        }}
        
        .thumbnail-card:hover .thumbnail-image img {{
            transform: scale(1.05);
        }}
        
        .thumbnail-info {{
            padding: 15px 20px;
            background: #f8f9fa;
            display: flex;
            justify-content: space-between;
            align-items: center;
            font-size: 0.9em;
            color: #6c757d;
        }}
        
        .modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.5);
        }}
        
        .modal-content {{
            background-color: white;
            margin: 5% auto;
            padding: 30px;
            border-radius: 15px;
            width: 80%;
            max-width: 600px;
            position: relative;
        }}
        
        .close {{
            color: #aaa;
            float: right;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
        }}
        
        .close:hover {{
            color: #000;
        }}
        
        .filters {{
            padding: 20px 30px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .filter-buttons {{
            display: flex;
            gap: 10px;
            flex-wrap: wrap;
        }}
        
        .filter-btn {{
            padding: 8px 16px;
            border: none;
            border-radius: 20px;
            background: #e9ecef;
            color: #495057;
            cursor: pointer;
            transition: all 0.3s ease;
        }}
        
        .filter-btn.active {{
            background: #667eea;
            color: white;
        }}
        
        .filter-btn:hover {{
            background: #5a6fd8;
            color: white;
        }}
        
        @media (max-width: 768px) {{
            .thumbnails-grid {{
                grid-template-columns: 1fr;
                padding: 15px;
            }}
            
            .summary-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📊 Relatório Visual de Dashboards</h1>
            <p>Assignment: {assignment_name} | Turma: {turma_name}</p>
        </div>
        
        <div class="summary">
            <h2>📈 Resumo Estatístico</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <h3>{correction_report.summary.get('total_submissions', 0)}</h3>
                    <p>Total de Submissões</p>
                </div>
                <div class="summary-item">
                    <h3>{correction_report.summary.get('average_score', 0):.1f}</h3>
                    <p>Nota Média</p>
                </div>
                <div class="summary-item">
                    <h3>{correction_report.summary.get('passing_rate', 0):.1%}</h3>
                    <p>Taxa de Aprovação</p>
                </div>
                <div class="summary-item">
                    <h3>{correction_report.summary.get('excellent_rate', 0):.1%}</h3>
                    <p>Taxa de Excelência</p>
                </div>
            </div>
        </div>
        
        <div class="filters">
            <h3>🔍 Filtros</h3>
            <div class="filter-buttons">
                <button class="filter-btn active" onclick="filterByScore('all')">Todos</button>
                <button class="filter-btn" onclick="filterByScore('excellent')">Excelente (9+)</button>
                <button class="filter-btn" onclick="filterByScore('good')">Bom (7-8.9)</button>
                <button class="filter-btn" onclick="filterByScore('pass')">Aprovado (6-6.9)</button>
                <button class="filter-btn" onclick="filterByScore('fail')">Reprovado (<6)</button>
            </div>
        </div>
        
        <div class="thumbnails-grid">
            {thumbnails_html}
        </div>
    </div>
    
    <!-- Modal para detalhes -->
    <div id="detailsModal" class="modal">
        <div class="modal-content">
            <span class="close" onclick="closeModal()">&times;</span>
            <h2 id="modalTitle"></h2>
            <div id="modalContent"></div>
        </div>
    </div>
    
    <script>
        function showDetails(name, score, tests, status) {{
            document.getElementById('modalTitle').textContent = name;
            document.getElementById('modalContent').innerHTML = `
                <p><strong>Nota:</strong> ${{score}}/10</p>
                <p><strong>Status:</strong> ${{status}}</p>
                <p><strong>Testes:</strong> ${{tests}}</p>
            `;
            document.getElementById('detailsModal').style.display = 'block';
        }}
        
        function closeModal() {{
            document.getElementById('detailsModal').style.display = 'none';
        }}
        
        function filterByScore(filter) {{
            const cards = document.querySelectorAll('.thumbnail-card');
            const buttons = document.querySelectorAll('.filter-btn');
            
            // Remove active class from all buttons
            buttons.forEach(btn => btn.classList.remove('active'));
            
            // Add active class to clicked button
            event.target.classList.add('active');
            
            cards.forEach(card => {{
                const score = parseFloat(card.querySelector('.score-badge').textContent.split(' ')[1]);
                let show = false;
                
                switch(filter) {{
                    case 'excellent':
                        show = score >= 9.0;
                        break;
                    case 'good':
                        show = score >= 7.0 && score < 9.0;
                        break;
                    case 'pass':
                        show = score >= 6.0 && score < 7.0;
                        break;
                    case 'fail':
                        show = score < 6.0;
                        break;
                    default:
                        show = true;
                }}
                
                card.style.display = show ? 'block' : 'none';
            }});
        }}
        
        // Close modal when clicking outside
        window.onclick = function(event) {{
            const modal = document.getElementById('detailsModal');
            if (event.target == modal) {{
                modal.style.display = 'none';
            }}
        }}
    </script>
</body>
</html>
""" 