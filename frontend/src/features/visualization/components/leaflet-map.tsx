"use client";

import React, { useEffect } from 'react';
import { MapContainer, ImageOverlay, useMap } from 'react-leaflet';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

interface LeafletMapProps {
  url: string;
  resetTrigger: number;
}

function ResetControl({ resetTrigger }: { resetTrigger: number }) {
  const map = useMap();
  useEffect(() => {
    // Center and fit the image bounds on reset
    map.fitBounds([[0, 0], [1000, 1000]]);
  }, [resetTrigger, map]);
  return null;
}

export default function LeafletMap({ url, resetTrigger }: LeafletMapProps) {
  // Use CRS.Simple for raw satellite imagery that isn't reprojected to Web Mercator.
  // This treats the map as a flat coordinate system (like an image viewer) 
  // so the globe doesn't awkwardly stretch over OpenStreetMap.
  const bounds: L.LatLngBoundsExpression = [[0, 0], [1000, 1000]];

  return (
    <MapContainer 
      crs={L.CRS.Simple}
      bounds={bounds} 
      className="w-full h-full z-0 bg-[#0a0a0a]"
      zoomControl={true}
      minZoom={-2}
      maxZoom={4}
      style={{ height: '100%', width: '100%', minHeight: '400px' }}
    >
      <ImageOverlay
        url={url}
        bounds={bounds}
        opacity={1}
        crossOrigin="anonymous"
        zIndex={10}
      />

      <ResetControl resetTrigger={resetTrigger} />
    </MapContainer>
  );
}