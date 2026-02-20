import React, { useState, useEffect } from 'react';
import { Droplets, Thermometer, Zap } from 'lucide-react';

interface TelemetryUpdate {
    type: string;
    timestamp: string;
    field_id: string;
    data: {
        sensor_id: string;
        moisture: number;
        temperature: number;
        status: string;
    };
}

const TelemetryOverlay: React.FC = () => {
    const [lastUpdate, setLastUpdate] = useState<TelemetryUpdate | null>(null);
    const [connected, setConnected] = useState(false);
    const [isVisible, setIsVisible] = useState(false);

    useEffect(() => {
        const ws = new WebSocket('ws://localhost:8000/api/v1/ws');

        ws.onopen = () => {
            console.log('Telemetry WebSocket connected');
            setConnected(true);
        };

        ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            if (data.type === 'SENSOR_UPDATE') {
                setLastUpdate(data);
                setIsVisible(true);
                // Hide after 4 seconds
                setTimeout(() => setIsVisible(false), 4000);
            }
        };

        ws.onclose = () => {
            console.log('Telemetry WebSocket disconnected');
            setConnected(false);
        };

        return () => ws.close();
    }, []);

    if (!connected && !lastUpdate) return null;

    return (
        <div className={`fixed bottom-6 right-6 z-50 transition-all duration-500 transform ${isVisible ? 'translate-y-0 opacity-100' : 'translate-y-12 opacity-0 pointer-events-none'}`}>
            <div className="bg-white/90 backdrop-blur-md rounded-2xl shadow-2xl border border-green-100 p-5 w-80">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-2">
                        <div className={`w-2 h-2 rounded-full ${connected ? 'bg-green-500 animate-pulse' : 'bg-red-500'}`} />
                        <span className="text-xs font-bold text-gray-500 uppercase tracking-widest">Live Telemetry</span>
                    </div>
                    <span className="text-[10px] text-gray-400 font-mono">
                        {lastUpdate ? new Date(lastUpdate.timestamp).toLocaleTimeString() : '--:--:--'}
                    </span>
                </div>

                {lastUpdate && (
                    <div className="space-y-4">
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="bg-blue-50 p-2 rounded-lg">
                                    <Droplets className="w-5 h-5 text-blue-500" />
                                </div>
                                <div>
                                    <p className="text-[10px] text-gray-400 uppercase font-bold">Moisture</p>
                                    <p className="text-lg font-bold text-gray-800">{(lastUpdate.data.moisture * 100).toFixed(1)}%</p>
                                </div>
                            </div>
                            <div className="flex items-center gap-3">
                                <div className="bg-orange-50 p-2 rounded-lg">
                                    <Thermometer className="w-5 h-5 text-orange-500" />
                                </div>
                                <div>
                                    <p className="text-[10px] text-gray-400 uppercase font-bold">Temp</p>
                                    <p className="text-lg font-bold text-gray-800">{lastUpdate.data.temperature}°C</p>
                                </div>
                            </div>
                        </div>

                        <div className="pt-3 border-t border-gray-100 flex items-center justify-between">
                            <div className="flex items-center gap-2">
                                <Zap className={`w-4 h-4 ${lastUpdate.data.status === 'alert' ? 'text-red-500' : 'text-green-500'}`} />
                                <span className={`text-xs font-bold ${lastUpdate.data.status === 'alert' ? 'text-red-600' : 'text-green-600'}`}>
                                    Sensor {lastUpdate.data.sensor_id}
                                </span>
                            </div>
                            <span className="text-[10px] bg-gray-100 px-2 py-0.5 rounded text-gray-500 font-medium">
                                {lastUpdate.field_id}
                            </span>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default TelemetryOverlay;
