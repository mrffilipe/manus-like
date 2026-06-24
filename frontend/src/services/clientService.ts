import { api } from '../config'
import type {
  ClientDetail,
  ClientListResponse,
  ClientResource,
  CreateClientPayload,
  CreateResourcePayload,
  UpdateClientPayload,
  UpdateResourcePayload,
} from '../types'
import { apiPaths } from './httpPaths'

export async function listClients(): Promise<ClientListResponse> {
  const response = await api.get<ClientListResponse>(apiPaths.clients)
  return response.data
}

export async function getClient(clientId: string): Promise<ClientDetail> {
  const response = await api.get<ClientDetail>(apiPaths.clientDetail(clientId))
  return response.data
}

export async function createClient(payload: CreateClientPayload): Promise<ClientDetail> {
  const response = await api.post<ClientDetail>(apiPaths.clients, payload)
  return response.data
}

export async function updateClient(clientId: string, payload: UpdateClientPayload): Promise<ClientDetail> {
  const response = await api.patch<ClientDetail>(apiPaths.clientDetail(clientId), payload)
  return response.data
}

export async function deleteClient(clientId: string): Promise<void> {
  await api.delete(apiPaths.clientDetail(clientId))
}

export async function createResource(
  clientId: string,
  payload: CreateResourcePayload,
): Promise<ClientResource> {
  const response = await api.post<ClientResource>(apiPaths.clientResources(clientId), payload)
  return response.data
}

export async function uploadResourceFile(
  clientId: string,
  file: File,
  title: string,
  category?: string,
): Promise<ClientResource> {
  const formData = new FormData()
  formData.append('title', title)
  formData.append('file', file)
  if (category) {
    formData.append('category', category)
  }
  const response = await api.post<ClientResource>(apiPaths.clientResourceUpload(clientId), formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return response.data
}

export async function updateResource(
  clientId: string,
  resourceId: string,
  payload: UpdateResourcePayload,
): Promise<ClientResource> {
  const response = await api.patch<ClientResource>(
    apiPaths.clientResourceDetail(clientId, resourceId),
    payload,
  )
  return response.data
}

export async function deleteResource(clientId: string, resourceId: string): Promise<void> {
  await api.delete(apiPaths.clientResourceDetail(clientId, resourceId))
}

export async function refreshResourceLink(clientId: string, resourceId: string): Promise<ClientResource> {
  const response = await api.post<ClientResource>(apiPaths.clientResourceRefresh(clientId, resourceId))
  return response.data
}
