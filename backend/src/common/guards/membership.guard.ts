import {
  CanActivate,
  ExecutionContext,
  ForbiddenException,
  Injectable,
} from '@nestjs/common';
import { Reflector } from '@nestjs/core';
import { PrismaService } from '../../prisma/prisma.service.js';
import { ROLES_KEY } from '../decorators/roles.decorator.js';
import type { MembershipRole } from '../../generated/prisma/enums.js';
import type { AuthenticatedRequest } from '../types/authenticated-request.js';

/**
 * Autorización a nivel de organización (multi-tenant + RBAC).
 *
 * Requiere ejecutarse después de JwtAuthGuard. Toma `organizationId` de los
 * parámetros de ruta, resuelve la Membership del usuario autenticado en esa
 * organización y, si el handler declara `@Roles(...)`, valida que el rol de
 * la Membership esté entre los permitidos. Deniega con 403 si el usuario no
 * pertenece a la organización o no tiene el rol requerido — nunca revela si
 * la organización existe, para no filtrar datos entre tenants.
 */
@Injectable()
export class MembershipGuard implements CanActivate {
  constructor(
    private readonly reflector: Reflector,
    private readonly prisma: PrismaService,
  ) {}

  async canActivate(context: ExecutionContext): Promise<boolean> {
    const request = context.switchToHttp().getRequest<AuthenticatedRequest>();
    const organizationId = request.params.organizationId;

    if (typeof organizationId !== 'string' || organizationId.length === 0) {
      throw new ForbiddenException(
        'La ruta no especifica una organización válida.',
      );
    }

    const membership = await this.prisma.membership.findUnique({
      where: {
        userId_organizationId: {
          userId: request.user.userId,
          organizationId,
        },
      },
    });

    if (!membership) {
      throw new ForbiddenException('No perteneces a esta organización.');
    }

    const requiredRoles = this.reflector.getAllAndOverride<
      MembershipRole[] | undefined
    >(ROLES_KEY, [context.getHandler(), context.getClass()]);

    if (
      requiredRoles &&
      requiredRoles.length > 0 &&
      !requiredRoles.includes(membership.role)
    ) {
      throw new ForbiddenException(
        'No tienes el rol necesario para esta acción.',
      );
    }

    request.membership = membership;
    return true;
  }
}
