document.addEventListener('DOMContentLoaded', () => {
    const container = document.getElementById('graph-container');
    if (!container) return;

    const isDark = document.documentElement.hasAttribute('data-theme');
    const colors = {
        node: '#3b82f6',
        link: isDark ? '#475569' : '#d6d3d1',
        label: isDark ? '#94a3b8' : '#78716c',
    };

    const width = container.clientWidth;
    const height = container.clientHeight;

    const svg = d3.select('#graph-container')
        .append('svg')
        .attr('width', width)
        .attr('height', height);

    fetch('/api/graph')
        .then(res => res.json())
        .then(data => {
            const simulation = d3.forceSimulation(data.nodes)
                .force('link', d3.forceLink(data.edges).id(d => d.slug).distance(80))
                .force('charge', d3.forceManyBody().strength(-200))
                .force('center', d3.forceCenter(width / 2, height / 2));

            const link = svg.append('g')
                .selectAll('line')
                .data(data.edges)
                .join('line')
                .attr('stroke', colors.link)
                .attr('stroke-width', 1);

            const node = svg.append('g')
                .selectAll('circle')
                .data(data.nodes)
                .join('circle')
                .attr('r', d => Math.max(4, Math.min(20, d.degree * 3 + 4)))
                .attr('fill', colors.node)
                .attr('cursor', 'pointer')
                .attr('stroke', isDark ? '#1e293b' : '#fff')
                .attr('stroke-width', 1.5)
                .on('click', (event, d) => {
                    window.location.href = '/note/' + d.slug;
                })
                .call(d3.drag()
                    .on('start', (event, d) => { if (!event.active) simulation.alphaTarget(0.3).restart(); d.fx = d.x; d.fy = d.y; })
                    .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y; })
                    .on('end', (event, d) => { if (!event.active) simulation.alphaTarget(0); d.fx = null; d.fy = null; })
                );

            const labels = svg.append('g')
                .selectAll('text')
                .data(data.nodes)
                .join('text')
                .text(d => d.title.length > 10 ? d.title.slice(0, 10) + '...' : d.title)
                .attr('font-size', 10)
                .attr('dx', 14)
                .attr('dy', 4)
                .attr('fill', colors.label)
                .style('pointer-events', 'none');

            simulation.on('tick', () => {
                link.attr('x1', d => d.source.x).attr('y1', d => d.source.y)
                    .attr('x2', d => d.target.x).attr('y2', d => d.target.y);
                node.attr('cx', d => d.x).attr('cy', d => d.y);
                labels.attr('x', d => d.x).attr('y', d => d.y);
            });
        });
});
