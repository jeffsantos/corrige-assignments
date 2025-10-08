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
        
        # Organiza thumbnails por índice (ordem de geração)
        submissions_with_thumbnails = []
        for i, submission in enumerate(correction_report.submissions):
            # Encontra thumbnail correspondente
            thumbnail = next((t for t in thumbnails if t.submission_identifier == 
                            (getattr(submission, 'github_login', None) or getattr(submission, 'group_name', None))), None)
            
            submissions_with_thumbnails.append({
                'submission': submission,
                'thumbnail': thumbnail,
                'index': i + 1
            })
        
        # Calcula estatísticas dos thumbnails
        thumbnail_stats = self._calculate_thumbnail_stats(thumbnails)
        
        # Gera HTML
        html_content = self._build_visual_html(
            assignment_name, turma_name, submissions_with_thumbnails, thumbnail_stats
        )
        
        # Salva arquivo
        output_file = output_dir / f"{assignment_name}_{turma_name}_visual.html"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return output_file
    
    def _calculate_thumbnail_stats(self, thumbnails: List[ThumbnailResult]) -> dict:
        """Calcula estatísticas dos thumbnails."""
        total = len(thumbnails)
        successful = sum(1 for t in thumbnails if t.streamlit_status == "success")
        failed = sum(1 for t in thumbnails if t.streamlit_status == "error")
        
        return {
            'total_thumbnails': total,
            'successful_thumbnails': successful,
            'failed_thumbnails': failed,
            'success_rate': successful / total if total > 0 else 0
        }
    
    def _build_visual_html(self, assignment_name: str, turma_name: str,
                          submissions_with_thumbnails: List[dict],
                          thumbnail_stats: dict) -> str:
        """Constrói o HTML do relatório visual."""
        
        # Gera grid de thumbnails
        thumbnails_html = ""
        for item in submissions_with_thumbnails:
            submission = item['submission']
            thumbnail = item['thumbnail']
            index = item['index']
            
            # Status do thumbnail
            thumbnail_status = "❌ Erro"
            thumbnail_status_class = "error"
            if thumbnail:
                if thumbnail.streamlit_status == "success":
                    thumbnail_status = "✅ Sucesso"
                    thumbnail_status_class = "success"
                elif thumbnail.streamlit_status == "timeout":
                    thumbnail_status = "⏰ Timeout"
                    thumbnail_status_class = "timeout"
                else:
                    thumbnail_status = f"❌ {thumbnail.error_message[:30]}..." if thumbnail.error_message else "❌ Erro"
            
            # Thumbnail ou placeholder
            # Exibe thumbnail se foi capturado com sucesso (arquivo existe), mesmo que haja erros de execução
            if thumbnail and thumbnail.thumbnail_path and thumbnail.thumbnail_path.exists():
                thumbnail_src = f"thumbnails/{thumbnail.thumbnail_path.name}"
                thumbnail_alt = f"Dashboard de {submission.display_name}"
                has_thumbnail = True
            else:
                thumbnail_src = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjIwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iMTAwJSIgaGVpZ2h0PSIxMDAlIiBmaWxsPSIjZjBmMGYwIi8+PHRleHQgeD0iNTAlIiB5PSI1MCUiIGZvbnQtZmFtaWx5PSJBcmlhbCwgc2Fucy1zZXJpZiIgZm9udC1zaXplPSIxNCIgZmlsbD0iIzk5OSIgdGV4dC1hbmNob3I9Im1pZGRsZSIgZHk9Ii4zZW0iPkRhc2hib2FyZCBuw6NvIGRpc3BvbsOtdmVsPC90ZXh0Pjwvc3ZnPg=="
                thumbnail_alt = "Dashboard não disponível"
                has_thumbnail = False
            
            # Evento de clique baseado na disponibilidade do thumbnail
            click_event = f"showThumbnailModal('{thumbnail_src}', '{submission.display_name}', {index})" if has_thumbnail else ""
            
            thumbnails_html += f"""
            <div class="thumbnail-card">
                <div class="thumbnail-header">
                    <h3>#{index} - {submission.display_name}</h3>
                </div>
                <div class="thumbnail-image">
                    <img src="{thumbnail_src}" alt="{thumbnail_alt}" onclick="{click_event}" style="cursor: {'pointer' if has_thumbnail else 'default'}">
                </div>
                <div class="thumbnail-info">
                    <div class="thumbnail-status {thumbnail_status_class}">{thumbnail_status}</div>
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
        }}
        
        .thumbnail-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 20px 40px rgba(0,0,0,0.15);
        }}
        
        .thumbnail-header {{
            padding: 20px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .thumbnail-header h3 {{
            font-size: 1.1em;
            color: #495057;
            margin: 0;
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
            justify-content: center;
            align-items: center;
            font-size: 0.9em;
            color: #6c757d;
        }}
        
        .thumbnail-status {{
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            font-weight: bold;
        }}
        
        .thumbnail-status.success {{
            background: #d4edda;
            color: #155724;
        }}
        
        .thumbnail-status.error {{
            background: #f8d7da;
            color: #721c24;
        }}
        
        .thumbnail-status.timeout {{
            background: #fff3cd;
            color: #856404;
        }}
        
        /* Modal para visualizar thumbnail em tamanho maior */
        .thumbnail-modal {{
            display: none;
            position: fixed;
            z-index: 1000;
            left: 0;
            top: 0;
            width: 100%;
            height: 100%;
            background-color: rgba(0,0,0,0.8);
            backdrop-filter: blur(5px);
        }}
        
        .thumbnail-modal-content {{
            position: relative;
            margin: 2% auto;
            padding: 20px;
            width: 90%;
            max-width: 1200px;
            max-height: 90vh;
            overflow: auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 25px 50px rgba(0,0,0,0.3);
        }}
        
        .thumbnail-modal-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 1px solid #e9ecef;
        }}
        
        .thumbnail-modal-header h2 {{
            color: #495057;
            font-size: 1.5em;
        }}
        
        .thumbnail-modal-close {{
            color: #aaa;
            font-size: 28px;
            font-weight: bold;
            cursor: pointer;
            background: none;
            border: none;
            padding: 0;
            width: 30px;
            height: 30px;
            display: flex;
            align-items: center;
            justify-content: center;
            border-radius: 50%;
            transition: all 0.3s ease;
        }}
        
        .thumbnail-modal-close:hover {{
            color: #000;
            background: #f8f9fa;
        }}
        
        .thumbnail-modal-image {{
            text-align: center;
            margin-bottom: 20px;
        }}
        
        .thumbnail-modal-image img {{
            max-width: 100%;
            max-height: 70vh;
            border-radius: 10px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}
        
        .thumbnail-modal-info {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        
        .thumbnail-modal-info h3 {{
            color: #495057;
            margin-bottom: 10px;
        }}
        
        .thumbnail-modal-info p {{
            color: #6c757d;
            margin: 5px 0;
        }}
        
        @media (max-width: 768px) {{
            .thumbnails-grid {{
                grid-template-columns: 1fr;
                padding: 15px;
            }}
            
            .summary-grid {{
                grid-template-columns: repeat(2, 1fr);
            }}
            
            .thumbnail-modal-content {{
                width: 95%;
                margin: 5% auto;
                padding: 15px;
            }}
            
            .thumbnail-modal-image img {{
                max-height: 60vh;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🖼️ Painel de Thumbnails</h1>
            <p>Assignment: {assignment_name} | Turma: {turma_name}</p>
        </div>
        
        <div class="summary">
            <h2>📊 Estatísticas dos Thumbnails</h2>
            <div class="summary-grid">
                <div class="summary-item">
                    <h3>{thumbnail_stats['total_thumbnails']}</h3>
                    <p>Total de Submissões</p>
                </div>
                <div class="summary-item">
                    <h3>{thumbnail_stats['successful_thumbnails']}</h3>
                    <p>Thumbnails Gerados</p>
                </div>
                <div class="summary-item">
                    <h3>{thumbnail_stats['failed_thumbnails']}</h3>
                    <p>Thumbnails com Erro</p>
                </div>
                <div class="summary-item">
                    <h3>{thumbnail_stats['success_rate']:.1%}</h3>
                    <p>Taxa de Sucesso</p>
                </div>
            </div>
        </div>
        
        <div class="thumbnails-grid">
            {thumbnails_html}
        </div>
    </div>
    
    <!-- Modal para visualizar thumbnail em tamanho maior -->
    <div id="thumbnailModal" class="thumbnail-modal">
        <div class="thumbnail-modal-content">
            <div class="thumbnail-modal-header">
                <h2 id="modalTitle">Visualizar Thumbnail</h2>
                <button class="thumbnail-modal-close" onclick="closeThumbnailModal()">&times;</button>
            </div>
            <div class="thumbnail-modal-image">
                <img id="modalImage" src="" alt="Thumbnail em tamanho maior">
            </div>
            <div class="thumbnail-modal-info">
                <h3 id="modalSubtitle">Informações</h3>
                <p id="modalIndex"></p>
                <p id="modalStatus"></p>
            </div>
        </div>
    </div>
    
    <script>
        function showThumbnailModal(imageSrc, submissionName, index) {{
            document.getElementById('modalTitle').textContent = submissionName;
            document.getElementById('modalImage').src = imageSrc;
            document.getElementById('modalImage').alt = `Thumbnail de ${{submissionName}}`;
            document.getElementById('modalSubtitle').textContent = submissionName;
            document.getElementById('modalIndex').textContent = `Submissão #${{index}}`;
            document.getElementById('modalStatus').textContent = '✅ Thumbnail gerado com sucesso';
            
            document.getElementById('thumbnailModal').style.display = 'block';
            document.body.style.overflow = 'hidden'; // Previne scroll da página
        }}
        
        function closeThumbnailModal() {{
            document.getElementById('thumbnailModal').style.display = 'none';
            document.body.style.overflow = 'auto'; // Restaura scroll da página
        }}
        
        // Fecha modal ao clicar fora dele
        window.onclick = function(event) {{
            const modal = document.getElementById('thumbnailModal');
            if (event.target == modal) {{
                closeThumbnailModal();
            }}
        }}
        
        // Fecha modal com tecla ESC
        document.addEventListener('keydown', function(event) {{
            if (event.key === 'Escape') {{
                closeThumbnailModal();
            }}
        }});
    </script>
</body>
</html>
""" 