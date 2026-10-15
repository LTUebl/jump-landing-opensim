/**
 * app.js
 * Interactive Plotly.js visualization and dashboard logic for
 * Jump Landing Biomechanics: OpenSim Inverse Kinetics & Muscle Forces
 * (BME 4903: Advanced Kinesiology / Biomechanics of Movement)
 */

let dataset = null;
let currentView = 'vgrf_bw';

const explanations = {
  vgrf_bw: `<strong>Vertical Ground Reaction Force (vGRF):</strong> Upright landing produces a sharper impact peak (4.45 BW vs 4.10 BW) and a loading rate nearly 3× higher (55.0 BW/s vs 18.6 BW/s). Forward trunk lean increases mechanical compliance, dissipating impact energy over more than double the absorption duration (0.43 s vs 0.17 s).`,
  knee_flexion: `<strong>Knee Flexion Kinematics:</strong> Forward lean landing exhibits deeper peak knee flexion (78.9° vs 54.0°), increasing the linear displacement of the center of mass during deceleration. Landing with shallow knee flexion (< 60°) combined with high impact force significantly elevates ACL strain.`,
  total_quads: `<strong>Total Quadriceps Force:</strong> The upright landing posture demands substantially higher total quadriceps extensor force (7,872 N vs 7,042 N) because the trunk remains erect, creating a large knee flexion moment that the quadriceps must eccentrically oppose.`,
  knee_extensors_detail: `<strong>Knee Extensor Muscle Breakdown:</strong> 
    <ul class="list-disc pl-5 mt-1 space-y-1">
      <li><strong>Vastus Lateralis (vaslat):</strong> Dominates extensor force production (4,831 N upright vs 3,526 N leaning) due to its large physiological cross-sectional area (PCSA).</li>
      <li><strong>Rectus Femoris (recfem):</strong> Generates nearly 70% higher peak force in the upright posture (1,270 N vs 749 N). As a biarticular muscle, rectus femoris is lengthened across the extended hip in upright landings, shifting it to a higher active tension zone on its force-length curve.</li>
      <li><strong>Vastus Medialis & Intermedius:</strong> Provide secondary extensor support and patellar tracking stability.</li>
    </ul>`,
  peak_bars: `<strong>Peak Loading Demands:</strong> Side-by-side comparison of normalized peak forces. Upright landing produces higher peak vertical ground reaction forces (4.45 BW) and greater quadriceps demand (8.45 BW), while forward lean landing spreads the impact over a compliant duration.`
};

async function init() {
  try {
    const res = await fetch('data/precomputed_curves.json');
    dataset = await res.json();
    renderChart(currentView);
  } catch (err) {
    console.error('Error loading precomputed curves:', err);
    document.getElementById('plot-area').innerHTML = `
      <div class="flex items-center justify-center h-full text-rose-600 text-sm font-semibold">
        Failed to load curve data. Please ensure 'data/precomputed_curves.json' is present.
      </div>
    `;
  }
}

function switchView(viewKey) {
  currentView = viewKey;
  
  // Update Tab Styling
  document.querySelectorAll('.tab-btn').forEach(btn => {
    btn.classList.remove('bg-white', 'text-blue-700', 'shadow-sm', 'font-bold');
    btn.classList.add('text-slate-600');
  });
  const activeBtn = document.getElementById(`tab-${viewKey}`);
  if (activeBtn) {
    activeBtn.classList.remove('text-slate-600');
    activeBtn.classList.add('bg-white', 'text-blue-700', 'shadow-sm', 'font-bold');
  }

  // Update Note Text
  const noteEl = document.getElementById('note-text');
  if (noteEl && explanations[viewKey]) {
    noteEl.innerHTML = explanations[viewKey];
  }

  renderChart(viewKey);
}

function renderChart(viewKey) {
  if (!dataset || !dataset.curves) return;
  const c = dataset.curves;
  const x = c.Percent_Landing_Phase;
  const plotArea = document.getElementById('plot-area');

  const baseLayout = {
    font: { family: 'Inter, sans-serif', color: '#1e293b' },
    margin: { l: 60, r: 30, t: 30, b: 50 },
    paper_bgcolor: 'transparent',
    plot_bgcolor: 'transparent',
    legend: { orientation: 'h', y: 1.15, x: 0.5, xanchor: 'center' },
    hovermode: 'x unified',
    xaxis: {
      title: '% Landing Absorption Phase (Initial Contact to Knee Max Flexion)',
      gridcolor: '#e2e8f0',
      zerolinecolor: '#cbd5e1'
    },
    yaxis: {
      gridcolor: '#e2e8f0',
      zerolinecolor: '#cbd5e1'
    }
  };

  const config = { responsive: true, displayModeBar: false };

  if (viewKey === 'vgrf_bw') {
    const traces = [
      {
        x: x,
        y: c.LeaningJump_vGRF_BW,
        name: 'Forward Lean Landing',
        type: 'scatter',
        mode: 'lines',
        line: { color: '#2563eb', width: 3 }
      },
      {
        x: x,
        y: c.UprightJump_vGRF_BW,
        name: 'Upright Landing',
        type: 'scatter',
        mode: 'lines',
        line: { color: '#dc2626', width: 3 }
      },
      {
        x: [0, 100],
        y: [1.0, 1.0],
        name: '1.0 Body Weight (BW)',
        type: 'scatter',
        mode: 'lines',
        line: { color: '#94a3b8', width: 1.5, dash: 'dot' }
      }
    ];
    baseLayout.yaxis.title = 'Total vGRF (Body Weights, BW)';
    Plotly.newPlot(plotArea, traces, baseLayout, config);
  } else if (viewKey === 'knee_flexion') {
    const traces = [
      {
        x: x,
        y: c.LeaningJump_KneeFlexion_deg,
        name: 'Forward Lean Landing',
        type: 'scatter',
        mode: 'lines',
        line: { color: '#2563eb', width: 3 }
      },
      {
        x: x,
        y: c.UprightJump_KneeFlexion_deg,
        name: 'Upright Landing',
        type: 'scatter',
        mode: 'lines',
        line: { color: '#dc2626', width: 3 }
      }
    ];
    baseLayout.yaxis.title = 'Knee Flexion Angle (degrees)';
    Plotly.newPlot(plotArea, traces, baseLayout, config);
  } else if (viewKey === 'total_quads') {
    const traces = [
      {
        x: x,
        y: c.LeaningJump_TotalQuads_N,
        name: 'Forward Lean Total Quads',
        type: 'scatter',
        mode: 'lines',
        line: { color: '#2563eb', width: 3 }
      },
      {
        x: x,
        y: c.UprightJump_TotalQuads_N,
        name: 'Upright Total Quads',
        type: 'scatter',
        mode: 'lines',
        line: { color: '#dc2626', width: 3 }
      }
    ];
    baseLayout.yaxis.title = 'Total Quadriceps Force (N)';
    Plotly.newPlot(plotArea, traces, baseLayout, config);
  } else if (viewKey === 'knee_extensors_detail') {
    const traces = [
      {
        x: x,
        y: c.LeaningJump_vaslat_N,
        name: 'vaslat (Leaning)',
        type: 'scatter',
        mode: 'lines',
        line: { color: '#1d4ed8', width: 2.5 }
      },
      {
        x: x,
        y: c.UprightJump_vaslat_N,
        name: 'vaslat (Upright)',
        type: 'scatter',
        mode: 'lines',
        line: { color: '#b91c1c', width: 2.5 }
      },
      {
        x: x,
        y: c.LeaningJump_recfem_N,
        name: 'recfem (Leaning)',
        type: 'scatter',
        mode: 'lines',
        line: { color: '#06b6d4', width: 2, dash: 'dash' }
      },
      {
        x: x,
        y: c.UprightJump_recfem_N,
        name: 'recfem (Upright)',
        type: 'scatter',
        mode: 'lines',
        line: { color: '#f59e0b', width: 2, dash: 'dash' }
      },
      {
        x: x,
        y: c.LeaningJump_vasmed_N,
        name: 'vasmed (Leaning)',
        type: 'scatter',
        mode: 'lines',
        line: { color: '#3b82f6', width: 1.5, dash: 'dot' }
      },
      {
        x: x,
        y: c.UprightJump_vasmed_N,
        name: 'vasmed (Upright)',
        type: 'scatter',
        mode: 'lines',
        line: { color: '#f87171', width: 1.5, dash: 'dot' }
      }
    ];
    baseLayout.yaxis.title = 'Individual Muscle Force (N)';
    Plotly.newPlot(plotArea, traces, baseLayout, config);
  } else if (viewKey === 'peak_bars') {
    const mass = 95.0;
    const bw_n = mass * 9.80665;
    const traces = [
      {
        x: ['Peak vGRF (BW)', 'Peak Quads (BW)', 'Vertical Impulse (BW·s)', 'Knee Flexion (x10°)'],
        y: [4.10, 7041.5 / bw_n, 0.79, 78.9 / 10],
        name: 'Forward Lean',
        type: 'bar',
        marker: { color: '#2563eb' }
      },
      {
        x: ['Peak vGRF (BW)', 'Peak Quads (BW)', 'Vertical Impulse (BW·s)', 'Knee Flexion (x10°)'],
        y: [4.45, 7871.6 / bw_n, 0.40, 54.0 / 10],
        name: 'Upright',
        type: 'bar',
        marker: { color: '#dc2626' }
      }
    ];
    baseLayout.barmode = 'group';
    baseLayout.xaxis.title = '';
    baseLayout.yaxis.title = 'Normalized Value';
    Plotly.newPlot(plotArea, traces, baseLayout, config);
  }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
