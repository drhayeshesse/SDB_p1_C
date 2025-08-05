document.addEventListener('DOMContentLoaded', () => {
    console.log('Dashboard JavaScript loaded successfully');
    
    // Check if all required elements exist
    const requiredElements = [
        '.tabs li',
        '.tab-content',
        '#card-cameras',
        '#card-streaming',
        '#card-buffer',
        '#card-health',
        '#card-cpu',
        '#card-ram',
        '#card-uptime',
        '#settings-form',
        '#cameras-table',
        '#logs-list'
    ];
    
    requiredElements.forEach(selector => {
        const element = document.querySelector(selector);
        if (!element) {
            console.error(`Missing element: ${selector}`);
        } else {
            console.log(`Found element: ${selector}`);
        }
    });
    // Tab functionality
    const tabs = document.querySelectorAll('.tabs li');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabs.forEach(tab => {
        tab.addEventListener('click', () => {
            const targetTab = tab.getAttribute('data-tab');
            
            // Remove active class from all tabs and contents
            tabs.forEach(t => t.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked tab and corresponding content
            tab.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
        });
    });
    
    // Load initial data
    loadStatus();
    loadSettings();
    loadCamerasTable();
    loadLogs();
    
    // Auto-refresh status every 5 seconds
    setInterval(loadStatus, 5000);
    
    // Status loading function
    async function loadStatus() {
        try {
            const res = await fetch('/api/status');
            const data = await res.json();
            
            document.querySelector('#card-cameras .card-value').textContent = `${data.activeCameras} / ${data.totalCameras}`;
            document.querySelector('#card-streaming .card-value').textContent = data.activeCameras > 0 ? 'Active' : 'Inactive';
            document.querySelector('#card-buffer .card-value').textContent = data.frame_buffer_status;
            document.querySelector('#card-health .card-value').textContent = data.activeCameras > 0 ? 'Good' : 'Warning';
            document.querySelector('#card-cpu .card-value').textContent = `${data.cpu || '--'}%`;
            document.querySelector('#card-ram .card-value').textContent = `${data.ram || '--'}%`;
            document.querySelector('#card-uptime .card-value').textContent = data.uptime;
        } catch (err) {
            console.error('Failed to load status', err);
        }
    }
  
    // Continue loadSettings()
    async function loadSettings() {
      try {
        const res = await fetch('/api/settings');
        const data = await res.json();
  
        document.getElementById('detectionEnabled').checked = data.detection.enabled;
        document.getElementById('schedulerEnabled').checked = data.detection.schedule_enabled;
        document.getElementById('detectionStart').value = data.detection.start_time || '22:00';
        document.getElementById('detectionEnd').value = data.detection.end_time || '06:00';
        document.getElementById('sensitivity').value = data.detection.sensitivity || 50;
        document.getElementById('motionThreshold').value = data.detection.motion_threshold || 0.35;
        document.getElementById('fps').value = data.processing.sleep_time ? (1 / data.processing.sleep_time).toFixed(1) : 1;
      } catch (err) {
        console.error("Failed to load settings", err);
      }
    }
  
    // Range input handlers
    document.getElementById('sensitivity').addEventListener('input', (e) => {
        document.getElementById('sensitivity-value').textContent = e.target.value;
    });
    
    document.getElementById('motionThreshold').addEventListener('input', (e) => {
        document.getElementById('motionThreshold-value').textContent = e.target.value;
    });
    
    // Handle settings form submission
    document.getElementById('settings-form').addEventListener('submit', async (e) => {
      e.preventDefault();
      
      const statusDiv = document.getElementById('settings-status');
      
      const payload = {
        enabled: document.getElementById('detectionEnabled').checked,
        schedule_enabled: document.getElementById('schedulerEnabled').checked,
        start_time: document.getElementById('detectionStart').value,
        end_time: document.getElementById('detectionEnd').value,
        sensitivity: parseInt(document.getElementById('sensitivity').value),
        motion_threshold: parseFloat(document.getElementById('motionThreshold').value),
        fps: parseFloat(document.getElementById('fps').value),
      };
  
      try {
        const res = await fetch('/api/settings/detection', {
          method: 'PUT',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(payload),
        });
  
        if (!res.ok) throw new Error('Failed to save settings');
  
        statusDiv.textContent = 'Settings saved successfully!';
        statusDiv.className = 'status-message success';
        setTimeout(() => {
            statusDiv.className = 'status-message';
        }, 3000);
      } catch (err) {
        console.error('Error saving settings:', err);
        statusDiv.textContent = 'Failed to save settings';
        statusDiv.className = 'status-message error';
        setTimeout(() => {
            statusDiv.className = 'status-message';
        }, 3000);
      }
    });
  
    // ---- Camera Settings ----
    async function loadCamerasTable() {
      try {
        const res = await fetch('/api/cameras');
        const cameras = await res.json();
  
        const tbody = document.querySelector('#cameras-table tbody');
        tbody.innerHTML = '';
  
        cameras.forEach(cam => {
          const tr = document.createElement('tr');
  
          tr.innerHTML = `
            <td>${cam.id}</td>
            <td>${cam.name}</td>
            <td>${cam.ip}</td>
            <td><span class="status-badge ${cam.status.toLowerCase()}">${cam.status}</span></td>
            <td>${cam.fps || '--'}</td>
            <td>
              <button data-id="${cam.id}" class="edit-btn">Edit</button>
              <button data-id="${cam.id}" class="delete-btn">Delete</button>
              <button data-id="${cam.id}" class="reload-btn">Reload</button>
            </td>
          `;
          tbody.appendChild(tr);
        });
  
        // Add event listeners for buttons
        document.querySelectorAll('.edit-btn').forEach(btn => {
          btn.onclick = () => {
            const id = btn.getAttribute('data-id');
            // TODO: Implement edit functionality (show form with data, send PUT)
            alert(`Edit camera ${id} - To be implemented`);
          };
        });
  
        document.querySelectorAll('.delete-btn').forEach(btn => {
          btn.onclick = async () => {
            const id = btn.getAttribute('data-id');
            if (confirm('Delete camera ' + id + '?')) {
              // TODO: Implement DELETE call
              alert(`Delete camera ${id} - To be implemented`);
            }
          };
        });
  
        document.querySelectorAll('.reload-btn').forEach(btn => {
          btn.onclick = async () => {
            const id = btn.getAttribute('data-id');
            // TODO: Implement reload action call to backend
            alert(`Reload camera ${id} - To be implemented`);
          };
        });
      } catch (err) {
        console.error('Failed to load cameras', err);
      }
    }
  
    // Add New Camera button
    document.getElementById('btn-add-camera').onclick = () => {
      alert('Add camera form - To be implemented');
    };
  
    // ---- Logs ----
    async function loadLogs(filter = 'uptime', groupBy = 'none') {
      try {
        const res = await fetch(`/api/events?since=${filter}&group_by=${groupBy}`);
        const data = await res.json();
  
        const ul = document.getElementById('logs-list');
        ul.innerHTML = '';
  
        if (data.grouped) {
          // Handle grouped logs
          Object.keys(data.groups).forEach(groupKey => {
            // Create group header
            const groupHeader = document.createElement('li');
            groupHeader.className = 'log-group-header';
            groupHeader.innerHTML = `
              <div class="group-title">
                <span class="group-icon">📁</span>
                <span class="group-name">${groupKey}</span>
                <span class="group-count">(${data.groups[groupKey].length} logs)</span>
              </div>
            `;
            ul.appendChild(groupHeader);
            
            // Add logs for this group
            data.groups[groupKey].forEach(log => {
              const li = document.createElement('li');
              li.className = 'log-item grouped';
              li.textContent = `[${new Date(log.timestamp).toLocaleTimeString()}] ${log.type.toUpperCase()}: ${log.message} (Camera ${log.camera_id || 'N/A'})`;
              li.classList.add('log-' + log.type);
              ul.appendChild(li);
            });
          });
        } else {
          // Handle flat list
          data.forEach(log => {
            const li = document.createElement('li');
            li.textContent = `[${new Date(log.timestamp).toLocaleTimeString()}] ${log.type.toUpperCase()}: ${log.message} (Camera ${log.camera_id || 'N/A'})`;
            li.classList.add('log-' + log.type);
            ul.appendChild(li);
          });
        }
      } catch (err) {
        console.error('Failed to load logs', err);
      }
    }
  
    // Log filter & refresh button
    document.getElementById('log-filter').onchange = (e) => {
      const groupBy = document.getElementById('log-group').value;
      loadLogs(e.target.value, groupBy);
    };
    
    document.getElementById('log-group').onchange = (e) => {
      const filter = document.getElementById('log-filter').value;
      loadLogs(filter, e.target.value);
    };
    
    document.getElementById('btn-refresh-logs').onclick = () => {
      const filter = document.getElementById('log-filter').value;
      const groupBy = document.getElementById('log-group').value;
      loadLogs(filter, groupBy);
    };
  
    // Camera feed functionality
    async function loadCameraFeeds() {
        try {
            const res = await fetch('/api/cameras');
            const cameras = await res.json();
            
            const feedsGrid = document.getElementById('feeds-grid');
            feedsGrid.innerHTML = '';
            
            cameras.forEach(cam => {
                const feedDiv = document.createElement('div');
                feedDiv.className = 'camera-feed';
                feedDiv.innerHTML = `
                    <h3>Camera ${cam.id} - ${cam.name}</h3>
                    <div class="feed-container">
                        <img src="/stream/${cam.id}/original" alt="Camera ${cam.id}" class="feed-image" />
                    </div>
                    <div class="feed-controls">
                        <button onclick="switchFeed(${cam.id}, 'original')" class="feed-btn active">Original</button>
                        <button onclick="switchFeed(${cam.id}, 'current')" class="feed-btn">Current</button>
                        <button onclick="switchFeed(${cam.id}, 'base')" class="feed-btn">Base</button>
                        <button onclick="switchFeed(${cam.id}, 'difference')" class="feed-btn">Difference</button>
                        <button onclick="switchFeed(${cam.id}, 'wasserstein')" class="feed-btn">Wasserstein</button>
                        <button onclick="switchFeed(${cam.id}, 'mean')" class="feed-btn">Mean</button>
                        <button onclick="switchFeed(${cam.id}, 'heatmap')" class="feed-btn">Heatmap</button>
                    </div>
                `;
                feedsGrid.appendChild(feedDiv);
            });
        } catch (err) {
            console.error('Failed to load camera feeds', err);
        }
    }
    
    // Switch camera feed type
    window.switchFeed = function(cameraId, feedType) {
        const feedImage = document.querySelector(`[onclick="switchFeed(${cameraId}, '${feedType}')"]`).closest('.camera-feed').querySelector('.feed-image');
        feedImage.src = `/stream/${cameraId}/${feedType}`;
        
        // Update active button
        const feedDiv = feedImage.closest('.camera-feed');
        feedDiv.querySelectorAll('.feed-btn').forEach(btn => btn.classList.remove('active'));
        feedDiv.querySelector(`[onclick="switchFeed(${cameraId}, '${feedType}')"]`).classList.add('active');
    };
    
    // Load camera feeds when liveview tab is clicked
    document.querySelector('[data-tab="liveview"]').addEventListener('click', loadCameraFeeds);
    
    // Initial load logs
    loadLogs();
  
  });